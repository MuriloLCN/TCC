from dataclasses import dataclass

@dataclass
class Indicadores:
    # Indicadores de Amorim e Veloso (excluindo divisões)
    num_tokens: int 
    num_prim_pessoa_sing: int
    num_pronomes_demonstrativos: int
    num_enclises: int
    num_erros_gramatica: int
    num_erros_ortografica: int
    num_erros_estilo: int
    num_sentencas_maiores_que_70_chars: int
    num_marcadores_discursivos: int
    num_palavras_diferentes: int
    flesch_score: float
    tamanho_medio_palavras_silabas: float
    similaridade_com_tema: float

    # Mais alguns indicadores, utilizados por Li et. al
    """
    numero de caracteres
    numero de palavras
    numero de simbolos de pontuacao
    numero de substantivos
    '' verbos
    '' adverbios
    '' adjetivos
    '' conjuncoes

    numero de sentencas
    tamanho medio das sentencas
    variancia no tamanho das sentencas

    numero de palavras do texto que aparecem no prompt
    """

@dataclass
class Redacao:
    id_redacao: int
    prompt: str
    textos_suporte: str
    texto_redacao: str
    notas: list[int]
    ano: int
    fonte: str
    indicadores_texto: Indicadores