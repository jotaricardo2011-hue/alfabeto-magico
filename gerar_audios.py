"""Gera as falas do Alfabeto Mágico em MP3 com voz neural (edge-tts).

Uso:  python gerar_audios.py          (só gera o que falta)
      python gerar_audios.py --tudo   (refaz tudo)
Os arquivos vão para audio/. As palavras precisam bater com PALAVRAS do index.html.
"""
import asyncio, sys
from pathlib import Path
import edge_tts

VOZ = "pt-BR-FranciscaNeural"
RATE, PITCH = "-8%", "+8Hz"   # mais devagar e um pouco mais aguda, para criança
PASTA = Path(__file__).parent / "audio"

PALAVRAS = {
    "A": "abelha", "B": "bola", "C": "casa", "D": "dado", "E": "elefante", "F": "foca",
    "G": "gato", "H": "hipopótamo", "I": "igreja", "J": "jacaré", "L": "leão", "M": "maçã",
    "N": "navio", "O": "ovo", "P": "pato", "Q": "queijo", "R": "rato", "S": "sol",
    "T": "tartaruga", "U": "uva", "V": "vaca", "X": "xícara", "Z": "zebra",
}
# grafia que a voz pronuncia certo
NOME_LETRA = {
    "A": "á", "B": "bê", "C": "cê", "D": "dê", "E": "é", "F": "éfe", "G": "gê", "H": "agá",
    "I": "i", "J": "jóta", "L": "éle", "M": "ême", "N": "êne", "O": "ó", "P": "pê", "Q": "quê",
    "R": "erre", "S": "ésse", "T": "tê", "U": "u", "V": "vê", "X": "xis", "Z": "zê",
}
ELOGIOS = ["Muito bem!", "Isso aí!", "Parabéns!", "Que esperto!", "Arrasou!", "Acertou!"]

# Sílabas: palavra (como no SILABAS do index.html, sem acento na chave) -> palavra falada
SIL_PALAVRAS = {
    "BOLA": "bola", "CASA": "casa", "DADO": "dado", "GATO": "gato", "PATO": "pato", "VACA": "vaca",
    "MACACO": "macaco", "SAPO": "sapo", "FOCA": "foca", "RATO": "rato", "LUA": "lua", "ZEBRA": "zebra",
    "JACARÉ": "jacaré", "BONECA": "boneca", "PIPA": "pipa", "COPO": "copo", "LIMÃO": "limão", "PERA": "pera",
    "TOMATE": "tomate", "CAVALO": "cavalo", "BANANA": "banana", "DEDO": "dedo", "MULA": "mula", "NUVEM": "nuvem",
}
# como a voz deve dizer cada 1ª sílaba sozinha
SIL_FALA = {
    "BO": "bó", "CA": "cá", "DA": "dá", "GA": "gá", "PA": "pá", "VA": "vá", "MA": "má", "SA": "sá",
    "FO": "fó", "RA": "rá", "LU": "lú", "ZE": "zé", "JA": "já", "PI": "pí", "CO": "có", "LI": "lí",
    "PE": "pê", "TO": "tô", "BA": "bá", "DE": "dê", "MU": "mú", "NU": "nú",
}
SIL_EXCECAO = {"BONECA": "bô"}  # mesma sílaba, outro som nesta palavra
SIL_PRIMEIRA = {"MACACO": "MA", "JACARÉ": "JA", "BONECA": "BO", "TOMATE": "TO", "CAVALO": "CA", "BANANA": "BA",
                "ZEBRA": "ZE", "LIMÃO": "LI", "NUVEM": "NU", "LUA": "LU"}

# Números: objeto -> (como falar, quantos/quantas)
OBJETOS = {"bolas": ("bolas", "Quantas"), "macas": ("maçãs", "Quantas"), "patinhos": ("patinhos", "Quantos"),
           "flores": ("flores", "Quantas"), "peixinhos": ("peixinhos", "Quantos"), "carrinhos": ("carrinhos", "Quantos"),
           "borboletas": ("borboletas", "Quantas"), "bananas": ("bananas", "Quantas")}
NUMEROS = ["um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez"]

# Cores
CORES = {"vermelho": "vermelho", "amarelo": "amarelo", "verde": "verde", "azul": "azul", "laranja": "laranja",
         "roxo": "roxo", "rosa": "rosa", "marrom": "marrom", "preto": "preto", "branco": "branco"}
COISAS = {"maca": "a maçã", "morango": "o morango", "banana": "a banana", "pintinho": "o pintinho", "sapo": "o sapo",
          "brocolis": "o brócolis", "baleia": "a baleia", "cenoura": "a cenoura", "laranja": "a laranja", "uva": "a uva",
          "berinjela": "a berinjela", "porquinho": "o porquinho", "flor": "a flor", "urso": "o urso",
          "chocolate": "o chocolate", "gato": "o gato", "nuvem": "a nuvem", "ovelha": "a ovelha"}

def falas():
    f = {}
    for l, p in PALAVRAS.items():
        n = NOME_LETRA[l]
        f[f"q_{l}"] = f"{p.capitalize()}. Com que letra começa {p}?"
        f[f"c_{l}"] = f"A letra {n}, de {p}!"
        f[f"e_{l}"] = f"Essa é a letra {n}. Tente de novo!"
    for chave, p in SIL_PALAVRAS.items():
        s = SIL_PRIMEIRA.get(chave, chave[:2])
        som = SIL_EXCECAO.get(chave, SIL_FALA[s])
        f[f"sq_{chave}"] = f"{p.capitalize()}. Com que sílaba começa {p}?"
        f[f"sc_{chave}"] = f"A sílaba {som}, de {p}!"
    for s, som in SIL_FALA.items():
        f[f"se_{s}"] = f"Essa é a sílaba {som}. Tente de novo!"
    for k, (nome, quantos) in OBJETOS.items():
        f[f"nq_{k}"] = f"{quantos} {nome} tem aqui? Conte comigo!"
    for i, n in enumerate(NUMEROS, 1):
        f[f"nc_{i}"] = "Tem um só!" if i == 1 else f"São {n}!"
        f[f"ne_{i}"] = f"Esse é o número {n}. Conte de novo!"
    for k, art in COISAS.items():
        nome = art.split(" ", 1)[1]
        f[f"kq_{k}"] = f"{nome.capitalize()}. De que cor é {art}?"
    for k, cor in CORES.items():
        f[f"kc_{k}"] = f"É {cor}! A cor {cor}!"
        f[f"ke_{k}"] = f"Essa é a cor {cor}. Tente de novo!"
    for i, e in enumerate(ELOGIOS):
        f[f"el_{i}"] = e
    f["fim_1"] = "Parabéns! Você ganhou uma estrela! Vamos tentar de novo?"
    f["fim_2"] = "Parabéns! Você ganhou duas estrelas!"
    f["fim_3"] = "Uau! Parabéns! Você ganhou três estrelas!"
    f["ola"] = "Olá! Vamos brincar?"
    return f

async def main():
    PASTA.mkdir(exist_ok=True)
    tudo = "--tudo" in sys.argv
    for nome, texto in falas().items():
        arq = PASTA / f"{nome}.mp3"
        if arq.exists() and not tudo:
            continue
        await edge_tts.Communicate(texto, VOZ, rate=RATE, pitch=PITCH).save(str(arq))
        print("ok", nome, "-", texto)

asyncio.run(main())
