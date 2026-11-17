# Testes com usuários

Objetivo: ver se as respostas do assistente são fáceis de entender e úteis para quem cuida de praças e espaços comunitários.

Como foi: pessoas do nosso convívio (família e vizinhos) fizeram perguntas ao assistente com as próprias palavras, a partir da situação "você cuida da iluminação de um espaço do seu bairro". Depois perguntamos se tinham entendido as respostas.

Data dos testes: 17/11/2026

Não guardamos nome nem dado pessoal. Cada pessoa tem só um código e o perfil geral.

## Registro dos testes

A coluna da resposta mostra o que o assistente respondeu na primeira vez, antes dos ajustes. "Entendeu?" e "Comentário" são o que cada pessoa nos disse.

| Código | Perfil | Pergunta feita | Primeira resposta do assistente | Entendeu? | Comentário da pessoa | Ajuste |
|---|---|---|---|---|---|---|
| P1 | Adulto, familiar de um integrante | "Aqui no condomínio a tarifa é 0,88 e as luzes da quadra ficam acesas 10 horas por noite. Vale a pena trocar para LED ou colocar painel solar para gastar menos?" | Usou a tarifa 0,88, mas mostrou só o tamanho do sistema solar, sem comparar com o LED | Sim | Disse que entendeu a resposta; sem outros comentários | Ajuste 1 |
| P2 | Adulto, familiar de um integrante | "A rua aqui do lado está muito escura e perigosa, já teve até assalto. Como faço para pedir melhoria de iluminação na prefeitura?" | Explicou como pedir à prefeitura (COSIP, 156), mas não citou a preocupação com segurança | Sim | Disse que entendeu a resposta; sem outros comentários | Ajuste 2 |
| P3 | Adulto, familiar de um integrante | "Considerando um hsp 5.2 na minha região, qual o tamanho do painel solar e da bateria necessários para alimentar o poste?" | Recalculou com HSP 5,2 (1 painel e 3 baterias), mas escreveu "1 painéis" | Sim | Disse que entendeu a resposta; sem outros comentários | Ajuste 3 |
| P4 | Adulto, familiar de um integrante | "Se a gente substituir as lâmpadas antigas da praça, qual vai ser o impacto ambiental real em redução de CO2?" | Informou cerca de 19 kg de CO2 por ano com LED e 25 kg com solar, e avisou que é pouco e que não conta fabricação e descarte | Sim | Disse que entendeu a resposta; sem outros comentários | Nenhum até agora |
| P5 | Adulto, familiar de um integrante | "Esses cálculos são confiáveis ou existe risco de a bateria não aguentar? Quais são as limitações dessa estimativa?" | Listou as limitações, mas não falou direto do risco da bateria | Sim | Disse que entendeu a resposta; sem outros comentários | Ajuste 4 |

## Ajustes realizados

Todos no arquivo `src/assistente.py`.

| Nº | Problema observado | O que mudamos |
|---|---|---|
| 1 | Pergunta que cita LED e painel solar juntos, ou "vale a pena", recebia só o tamanho do sistema solar | Agora o assistente compara as três opções (lâmpada atual, LED e LED com solar) |
| 2 | Quem fala de insegurança ao pedir melhoria na prefeitura não recebia nenhuma menção a isso | A resposta começa reconhecendo a preocupação, diz que iluminação ajuda mas não resolve sozinha e sugere registrar a ocorrência na polícia |
| 3 | Texto com "1 painéis" | Passou a escrever "1 painel" e "2 painéis" (e o mesmo para bateria) |
| 4 | Pergunta sobre risco da bateria não tinha resposta direta | A lista de limitações agora diz que a bateria foi calculada para 2 dias seguidos sem sol e que, passando disso, a luz pode apagar |

Depois dos ajustes, rodamos de novo as 5 perguntas e as respostas ficaram como esperado.

## Síntese

Cinco adultos do nosso convívio (familiares de um integrante) testaram o assistente em 17/11/2026. Todos disseram que entenderam as respostas e ninguém apontou termo confuso. Mesmo assim, ao rodar as perguntas no assistente, a gente percebeu quatro pontos que podiam melhorar (tabela de ajustes) e corrigiu todos. Os ajustes vieram dessa conferência do grupo, e não de reclamações das pessoas.

Limitações do teste: foram poucas pessoas, todas adultas e conhecidas, então não sabemos como crianças, idosos ou quem não conhece o assunto reagiriam. Também não testamos o assistente com quem de fato cuida de uma praça.
