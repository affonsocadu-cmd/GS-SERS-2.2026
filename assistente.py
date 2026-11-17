"""
Assistente do módulo de energia (Citizen Assist AI).

Rodar:  python assistente.py
Ou com uma pergunta só:  python assistente.py "qual o tamanho do painel solar?"
"""

import re
import sys
import unicodedata

import calculos as c

# valores que o usuário pode mudar durante a conversa
config = {"tarifa": c.TARIFA, "hsp": c.HSP, "horas": c.HORAS_NOITE, "anos": c.ANOS}

AJUDA = (
    "Eu ajudo com a iluminação de praças e espaços comunitários. Pode perguntar:\n"
    "- como iluminar a praça gastando menos?\n"
    "- qual o tamanho do painel solar?\n"
    "- quanto eu economizo com LED?\n"
    "- qual o impacto ambiental?\n"
    "- quais as limitações? / quais as fontes?\n"
    "- como peço melhoria para a prefeitura?\n"
    "Também dá pra mudar os valores, por exemplo: tarifa 0,78 | hsp 4,5 | horas 12 | anos 15"
)

AVISO = (
    "Atenção: esses valores são estimativas, não garantia de economia. "
    "A tarifa está sem tributos, então a conta real é um pouco maior. "
    "Fontes e limitações: pergunte 'fontes' ou 'limitações'."
)

LIMITES = (
    "Limitações dos cálculos:\n"
    "- são estimativas, não garantem economia nem geração de energia;\n"
    "- a tarifa usada não inclui tributos (ICMS e PIS/COFINS);\n"
    "- a bateria foi calculada para 2 dias seguidos sem sol; se passar disso a luz pode apagar;\n"
    "- dias nublados e sombra reduzem a geração dos painéis;\n"
    "- preços mudam conforme fornecedor e época;\n"
    "- em praça pública quem instala é a prefeitura; em espaço comunitário precisa de "
    "autorização de quem cuida do local;\n"
    "- iluminação ajuda na sensação de segurança, mas não garante menos crimes."
)

FONTES = (
    "Fontes dos dados: tabela de tarifas da Enel SP (REH 3.596/2026 da ANEEL), "
    "MCTI/SIRENE (fator de emissão), CRESESB (irradiação solar e Manual de Engenharia FV), "
    "datasheets dos fabricantes e orçamentos de mercado. A lista completa está no README."
)

PREFEITURA = (
    "Em ruas e praças públicas, a iluminação é responsabilidade da prefeitura, que cobra a "
    "COSIP (Contribuição de Iluminação Pública) na conta de luz. Você pode abrir um pedido "
    "nos canais da prefeitura (em São Paulo, o 156), informando o endereço, o problema e, se "
    "der, uma foto. Se o espaço for particular ou de uma associação, quem decide é o "
    "responsável pelo local."
)


PREFEITURA_SEGURANCA = (
    "Entendo a preocupação com a segurança. Iluminação ajuda na sensação de segurança, mas "
    "não resolve sozinha, e se houve crime também vale registrar a ocorrência na polícia. "
    "Sobre a iluminação:\n\n"
)


def sem_acento(texto):
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(ch for ch in texto if unicodedata.category(ch) != "Mn")


def tem(texto, palavras):
    for p in palavras:
        if p in texto:
            return True
    return False


def qtd(n, um, varios):
    return f"{n} {um if n == 1 else varios}"


def reais(valor):
    return "R$ " + f"{valor:,.0f}".replace(",", ".")


def num(valor, casas=2):
    return f"{valor:.{casas}f}".replace(".", ",")


def texto_payback(p, anos):
    if p is None:
        return "não se paga"
    txt = f"{p:.1f} anos".replace(".", ",")
    if p > anos:
        txt += f" (mais que os {anos} anos analisados)"
    return txt


def ler_ajustes(texto):
    mudou = []
    for nome in config:
        achou = re.search(nome + r"\D{0,12}?(\d+(?:[.,]\d+)?)", texto)
        if achou:
            valor = float(achou.group(1).replace(",", "."))
            if nome == "anos":
                valor = int(valor)
            config[nome] = valor
            mudou.append(f"{nome} = {valor:g}".replace(".", ","))
    return mudou


def resp_comparacao(base, led, solar, dim):
    anos = config["anos"]
    menor = min([base, led, solar], key=lambda x: x["custo_total"])
    return (
        f"Comparei 3 opções para um ponto de luz aceso {config['horas']:g} h por noite, em {anos} anos:\n"
        f"- Lâmpada atual: {reais(base['custo_total'])} no total.\n"
        f"- LED: {reais(led['custo_total'])}, se paga em {texto_payback(led['payback'], anos)}.\n"
        f"- LED + solar: {reais(solar['custo_total'])}, se paga em {texto_payback(solar['payback'], anos)}. "
        f"Precisa de {qtd(dim['n_paineis'], 'painel', 'painéis')} de {c.PAINEL_WP} Wp e "
        f"{qtd(dim['n_baterias'], 'bateria', 'baterias')}.\n\n"
        f"A opção mais barata nessa simulação: {menor['nome']}.\n\n" + AVISO
    )


def resp_solar(solar, dim):
    return (
        f"O LED de {c.POTENCIA_LED} W aceso {config['horas']:g} h por noite gasta "
        f"{num(dim['energia_dia'])} kWh por dia.\n"
        f"Pelo cálculo precisa de uns {dim['painel_wp']:.0f} Wp de painel "
        f"(HSP {num(config['hsp'])}, rendimento {num(c.RENDIMENTO, 3)}) e {num(dim['bateria_wh'] / 1000)} kWh "
        f"de bateria ({c.AUTONOMIA} dias de autonomia).\n"
        f"Com os módulos que existem à venda: {qtd(dim['n_paineis'], 'painel', 'painéis')} de {c.PAINEL_WP} Wp e "
        f"{qtd(dim['n_baterias'], 'bateria', 'baterias')} LiFePO4 de {dim['bateria_ah']:.0f} Ah (12,8 V), "
        f"cada painel com um controlador MPPT de 10 A.\n"
        f"Investimento estimado: {reais(solar['invest'])}. As baterias precisam ser trocadas "
        f"em cerca de {c.VIDA_BATERIA} anos.\n\n" + AVISO
    )


def resp_led(base, led):
    reducao = (1 - led["kwh"] / base["kwh"]) * 100
    anos = config["anos"]
    return (
        f"Trocar a lâmpada atual ({c.POTENCIA_ATUAL} W) por LED ({c.POTENCIA_LED} W) reduz o "
        f"consumo em cerca de {reducao:.0f}%: de {base['kwh']:.0f} para {led['kwh']:.0f} kWh por ano.\n"
        f"O custo por ano cai de {reais(base['custo_ano'])} para {reais(led['custo_ano'])}. "
        f"A luminária custa {reais(led['invest'])} instalada e se paga em "
        f"{texto_payback(led['payback'], anos)}.\n\n" + AVISO
    )


def resp_ambiental(led, solar):
    return (
        f"Em relação à lâmpada atual, o LED evita cerca de {led['co2_evitado']:.0f} kg de CO2 por ano "
        f"e o LED solar cerca de {solar['co2_evitado']:.0f} kg, usando o fator médio do sistema "
        f"elétrico brasileiro ({num(c.FATOR_EMISSAO, 4)} kg CO2/kWh).\n"
        "É pouco porque a energia do Brasil já tem muita fonte renovável. A solar faz mais "
        "diferença onde não tem rede elétrica. Esses números não contam a fabricação e o "
        "descarte de painéis e baterias, que também têm impacto."
    )


def responder(pergunta):
    texto = sem_acento(pergunta)
    mudou = ler_ajustes(texto)
    base, led, solar, dim = c.comparar(**config)
    inicio = ""
    if mudou:
        inicio = "Valores atualizados: " + ", ".join(mudou) + ".\n\n"

    if texto.strip(" ?!.") in ("ajuda", "help", "menu") or "o que voce faz" in texto:
        corpo = AJUDA
    elif tem(texto, ["prefeitura", "cosip", "solicitar", "reclamar", "156"]):
        corpo = PREFEITURA
        if tem(texto, ["assalto", "perigo", "escur", "crime", "inseguro", "seguranca"]):
            corpo = PREFEITURA_SEGURANCA + corpo
    elif tem(texto, ["limita", "garant", "risco", "certeza"]):
        corpo = LIMITES
    elif tem(texto, ["fonte", "referencia", "origem"]):
        corpo = FONTES
    elif tem(texto, ["ambient", "co2", "emiss", "carbono", "sustent"]):
        corpo = resp_ambiental(led, solar)
    elif (tem(texto, ["led"]) and tem(texto, ["solar", "painel"])) or tem(texto, ["vale a pena", "compensa", "comparar"]):
        corpo = resp_comparacao(base, led, solar, dim)
    elif tem(texto, ["solar", "painel", "bateria", "fotovolt"]):
        corpo = resp_solar(solar, dim)
    elif tem(texto, ["led", "lampada", "trocar"]):
        corpo = resp_led(base, led)
    elif tem(texto, ["seguranca", "crime", "assalto", "escuro"]):
        corpo = ("Uma praça bem iluminada pode ajudar na sensação de segurança, mas os estudos "
                 "mostram resultados variados e a iluminação sozinha não resolve. Sobre gastar "
                 "menos energia:\n\n" + resp_comparacao(base, led, solar, dim))
    elif tem(texto, ["comparar", "gastar", "economi", "iluminar", "custo", "praca", "vale"]) or mudou:
        corpo = resp_comparacao(base, led, solar, dim)
    else:
        corpo = "Não entendi a pergunta.\n\n" + AJUDA
    return inicio + corpo


def main():
    if len(sys.argv) > 1:
        print(responder(" ".join(sys.argv[1:])))
        return

    print("Citizen Assist AI - módulo de energia (digite 'ajuda' ou 'sair')\n")
    while True:
        try:
            pergunta = input("Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if pergunta == "":
            continue
        if sem_acento(pergunta) in ("sair", "exit"):
            break
        print("\nAssistente:", responder(pergunta), "\n")


if __name__ == "__main__":
    main()
