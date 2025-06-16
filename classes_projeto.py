from dataclasses import dataclass

@dataclass
class Indicadores:
    # Indicadores de Amorim e Veloso (excluindo divisões)
    num_tokens: int 
    num_prim_pessoa_sing: int
    num_pronomes_demonstrativos: int
    num_enclises: int
    num_erros_gramatica: int
    num_erros_ortografia: int
    num_erros_estilo: int
    num_sentencas_maiores_que_70_chars: int
    num_marcadores_discursivos: int
    num_palavras_diferentes: int
    flesch_score: float
    tamanho_medio_palavras_silabas: float
    similaridade_com_tema: float

    # Indicadores Li et al.

    tamanho_medio_sentencas: float
    variancia_tamanho_sentencas: float

    numero_substantivos: int
    numero_adverbios: int
    numero_adjetivos: int
    numero_conjuncoes: int

    # Indicadores propostos

    similaridade_declaracao_direitos_humanos: float
    similaridade_cap_1_constituicao_88: float
    
@dataclass
class Redacao:
    id_redacao: int
    prompt: str
    texto_suporte: str
    texto_redacao: str
    notas: list[int]
    indicadores_texto: Indicadores