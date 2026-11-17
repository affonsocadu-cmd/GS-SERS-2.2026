"""
Cálculos de energia da iluminação da praça (Citizen Assist AI).

Compara 3 situações para o mesmo ponto de luz:
  base  -> lâmpada atual de vapor de sódio (150 W)
  led   -> troca por luminária LED (40 W)
  solar -> LED ligado em painel solar + bateria (sem usar a rede)

Os dados e as fontes estão explicados no README (seção 7).
"""

import math

# ---------- dados de entrada ----------
POTENCIA_ATUAL = 150      # W
POTENCIA_LED = 40         # W
HORAS_NOITE = 10          # acesa das 19h às 5h
DIAS_ANO = 365
ANOS = 10                 # período da comparação

TARIFA = (283.45 + 190.17) / 1000   # R$/kWh, Enel SP, classe B4b, SEM tributos
FATOR_EMISSAO = 0.0461              # kg CO2 por kWh (SIN, 2025)

HSP = 3.84                          # estimado, pior mês em São Paulo
RENDIMENTO = 0.98 * 0.92 * 0.90 * 0.98   # controlador x bateria x módulo x cabos
AUTONOMIA = 2                       # dias
DOD = 0.80                          # profundidade de descarga da bateria
TENSAO = 12.8                       # V

PAINEL_WP = 100
PAINEL_PRECO = 350
BATERIA_WH = 384
BATERIA_PRECO = 690
CONTROLADOR_PRECO = 380
POSTE_PRECO = 820
VIDA_BATERIA = 8                    # anos

LED_PRECO = 350                     # luminária já instalada
MANUT_LED = 20                      # R$/ano
MANUT_SOLAR = 60                    # R$/ano


def consumo_anual(potencia, horas):
    # kWh por ano
    return potencia / 1000 * horas * DIAS_ANO


def dimensionar_solar(horas=HORAS_NOITE, hsp=HSP):
    energia_dia = POTENCIA_LED / 1000 * horas              # kWh por dia
    painel = energia_dia * 1000 / (hsp * RENDIMENTO)       # Wp necessário
    bateria = energia_dia * AUTONOMIA / DOD * 1000         # Wh necessário

    # como só existem módulos prontos, arredonda pra cima
    n_paineis = math.ceil(round(painel / PAINEL_WP, 6))
    n_baterias = math.ceil(round(bateria / BATERIA_WH, 6))

    return {
        "energia_dia": energia_dia,
        "painel_wp": painel,
        "bateria_wh": bateria,
        "n_paineis": n_paineis,
        "n_baterias": n_baterias,
        "bateria_ah": BATERIA_WH / TENSAO,
    }


def comparar(tarifa=TARIFA, hsp=HSP, horas=HORAS_NOITE, anos=ANOS):
    dim = dimensionar_solar(horas, hsp)

    custo_baterias = dim["n_baterias"] * BATERIA_PRECO
    invest_solar = (dim["n_paineis"] * (PAINEL_PRECO + CONTROLADOR_PRECO)
                    + custo_baterias + POSTE_PRECO)
    trocas = max(0, math.ceil(anos / VIDA_BATERIA) - 1)

    base = {"nome": "Lâmpada atual", "invest": 0,
            "kwh": consumo_anual(POTENCIA_ATUAL, horas),
            "manut": 0, "reposicao": 0}
    led = {"nome": "LED", "invest": LED_PRECO,
           "kwh": consumo_anual(POTENCIA_LED, horas),
           "manut": MANUT_LED, "reposicao": 0}
    solar = {"nome": "LED + solar", "invest": invest_solar,
             "kwh": 0,
             "manut": MANUT_SOLAR, "reposicao": trocas * custo_baterias}

    for op in (base, led, solar):
        op["custo_ano"] = op["kwh"] * tarifa + op["manut"]
        op["custo_total"] = op["invest"] + op["custo_ano"] * anos + op["reposicao"]
        op["co2_kg"] = op["kwh"] * FATOR_EMISSAO

    # payback e CO2 evitado, sempre comparando com a lâmpada atual
    base["payback"] = None
    base["co2_evitado"] = 0
    for op in (led, solar):
        economia = base["custo_ano"] - op["custo_ano"]
        if economia > 0:
            op["payback"] = op["invest"] / economia
        else:
            op["payback"] = None
        op["co2_evitado"] = base["co2_kg"] - op["co2_kg"]

    return base, led, solar, dim


def mostrar_tabela(base, led, solar, anos=ANOS):
    print(f"\nComparação em {anos} anos\n")
    print(f"{'Opção':<16}{'Invest. (R$)':>13}{'kWh/ano':>10}{'Custo/ano':>11}{'Total (R$)':>12}{'Payback':>12}")
    print("-" * 74)
    for op in (base, led, solar):
        if op["payback"] is None:
            pb = "-"
        else:
            pb = f"{op['payback']:.1f} anos"
        print(f"{op['nome']:<16}{op['invest']:>13,.0f}{op['kwh']:>10,.0f}"
              f"{op['custo_ano']:>11,.0f}{op['custo_total']:>12,.0f}{pb:>12}")


if __name__ == "__main__":
    base, led, solar, dim = comparar()
    mostrar_tabela(base, led, solar)
    print(f"\nSolar: {dim['n_paineis']} painéis de {PAINEL_WP} Wp e "
          f"{dim['n_baterias']} baterias de {dim['bateria_ah']:.0f} Ah")
    print(f"CO2 evitado por ano: LED {led['co2_evitado']:.0f} kg, solar {solar['co2_evitado']:.0f} kg")
