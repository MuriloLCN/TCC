from classes_projeto import *
from constantes_longas import marcadores_discursivos, titulo_1_constituicao_88, declaracao_direitos_humanos
from sentence_transformers import SentenceTransformer, util
import spacy
import statistics
import pyphen
import language_tool_python

tool = language_tool_python.LanguageTool('pt-BR')
hyphenator = pyphen.Pyphen(lang='pt_BR')
model = SentenceTransformer("alfaneo/bertimbau-base-portuguese-sts")

lista_pronomes_prim_pessoa_sing = ["eu", "me", "mim", "comigo", "meu", "minha", "meus", "minhas"]
pronomes_enclise = ["me", "te", "se", "lhe", "nos", "vos", "lhes", "o", "a", "os", "as"]

pln = spacy.load("pt_core_news_sm")

def _indicadores_spacy(dados_redacao: Redacao):
    tokens = pln(dados_redacao.texto_redacao)

    dados_redacao.indicadores_texto.num_tokens = len(tokens)
    
    # -- P/ calcular o tamanho médio e a variância
    tamanhos_sentencas_caracteres = []

    # -- P/ calcular o tamanho médio e a pontuação Flesch adaptada
    tamanhos_silabas = []
    tamanhos_sentencas_palavras = []
    numero_palavras = 0

    conjunto_palavras_distintas = set()

    # -- Indicadores que usam o SpaCy
    for sentenca in tokens.sents:

        tamanho = len(sentenca.text.strip())
        
        if tamanho > 70:
            # print(f"Sentenca maior que 70 chars: {sentenca.text}")
            dados_redacao.indicadores_texto.num_sentencas_maiores_que_70_chars += 1

        tamanhos_sentencas_caracteres.append(tamanho)
        tamanhos_sentencas_palavras.append(len(sentenca.text.split()))

    # -- Tamanho médio e variância das sentenças
    dados_redacao.indicadores_texto.tamanho_medio_sentencas = statistics.mean(tamanhos_sentencas_caracteres)
    dados_redacao.indicadores_texto.variancia_tamanho_sentencas = statistics.variance(tamanhos_sentencas_caracteres)

    print(f"Tamanhos sentencas: {str(tamanhos_sentencas_palavras)}  Tamanho med: {dados_redacao.indicadores_texto.tamanho_medio_sentencas}  Variancia: {dados_redacao.indicadores_texto.variancia_tamanho_sentencas}")

    for token in tokens:
        # print(f"{token.text} {token.pos_} {token.morph}")

        # -- Número de verbos da primeira pessoa do singular
        if token.pos_ == "VERB" and "1" in token.morph.get("Person") and "Sing" in token.morph.get("Number"):
            dados_redacao.indicadores_texto.num_prim_pessoa_sing += 1
        
        # -- Número de pronomes na primeira pessoa do singular
        if token.text.lower() in lista_pronomes_prim_pessoa_sing:
            dados_redacao.indicadores_texto.num_prim_pessoa_sing += 1

        # -- Número de pronomes demonstrativos
        if token.pos_ == "PRON" and "Dem" in token.morph.get("PronType"):
            dados_redacao.indicadores_texto.num_pronomes_demonstrativos += 1

        # -- Número de ênclises    
        if "-" in token.text and token.pos_ == "VERB":
            pronome = token.text.split("-")[1]
            if pronome in pronomes_enclise:
                dados_redacao.indicadores_texto.num_enclises += 1

        if token.is_alpha:
            # -- Contagem de palavras diferentes
            conjunto_palavras_distintas.add(token.text.lower())

            palavra_separada_silabas = hyphenator.inserted(token.text)
            numero_palavras += 1
            tamanhos_silabas.append(len(palavra_separada_silabas.split('-')))
            # print(f"{token.text}: {len(palavra_separada_silabas.split('-'))}")
            pass
            
        # -- Contagem de classes gramaticais
        if token.pos_ == "NOUN":
            dados_redacao.indicadores_texto.numero_substantivos += 1
        elif token.pos_ == "ADV":
            dados_redacao.indicadores_texto.numero_adverbios += 1
        elif token.pos_ == "ADJ":
            dados_redacao.indicadores_texto.numero_adjetivos += 1
        elif token.pos_ == "CCONJ" or token.pos_ == "SCONJ":
            dados_redacao.indicadores_texto.numero_conjuncoes += 1

    # print(f"Tamanhos silabas: {tamanhos_silabas}  Numero palavras: {numero_palavras}")

    dados_redacao.indicadores_texto.num_palavras_diferentes = len(conjunto_palavras_distintas)

    for sentenca in tokens.sents:
        texto = sentenca.text

        # Os marcadores estão ordenados por maior número de palavras até o menor
        for marcador in marcadores_discursivos:
            if marcador in texto:
                # Remover p/ evitar duplicatas
                # Ex: "X bem como Y" ativaria tanto p/ "bem como" tanto como "como" 
                texto = texto.replace(marcador, "")
                dados_redacao.indicadores_texto.num_marcadores_discursivos += 1

    # Flesch PT (Martins et al., 1996)
    # Score = 206.835 - 84.6 * med_silabas_por_palavra - 1.015 * med_palavras_por_sentenca + 42

    dados_redacao.indicadores_texto.flesch_score = 206.835 - 84.6 * statistics.mean(tamanhos_silabas) - 1.015 * statistics.mean(tamanhos_sentencas_palavras) + 42


def _calculo_similaridade(texto_a: str, texto_b: str):
    emb_a = model.encode(texto_a, convert_to_tensor=True)
    emb_b = model.encode(texto_b, convert_to_tensor=True)

    similaridade = util.cos_sim(emb_a, emb_b).item()
    print(f"Similaridade cosseno: {similaridade:.4f}")
    return similaridade


def _indicadores_similaridade(dados_redacao: Redacao):
    dados_redacao.indicadores_texto.similaridade_com_tema = _calculo_similaridade(dados_redacao.texto_redacao,dados_redacao.prompt)

    dados_redacao.indicadores_texto.similaridade_cap_1_constituicao_88 = _calculo_similaridade(dados_redacao.texto_redacao, titulo_1_constituicao_88)

    dados_redacao.indicadores_texto.similaridade_declaracao_direitos_humanos = _calculo_similaridade(dados_redacao.texto_redacao, declaracao_direitos_humanos)


def _indicadores_language_tool(dados_redacao: Redacao):
    erros = tool.check(dados_redacao.texto_redacao)

    for erro in erros:
        if erro.ruleIssueType == "misspelling":
            dados_redacao.indicadores_texto.num_erros_ortografia += 1
        elif erro.ruleIssueType == "style":
            dados_redacao.indicadores_texto.num_erros_estilo += 1
        elif erro.ruleIssueType == "grammar":
            dados_redacao.indicadores_texto.num_erros_gramatica += 1
        elif erro.ruleIssueType == "uncategorized":
            if erro.ruleId == "VERB_COMMA_CONJUNCTION":
                # A maior fatia dos não-categorizados são desse tipo, sendo erros de gramática
                print("Achou um erro de VERB COMMA CONJUNCTION")
                dados_redacao.indicadores_texto.num_erros_gramatica += 1
            else:
                # Das demais, a maioria são paronímias, onde se assume que a palavra foi escrita errada, sendo um erro de ortografia
                dados_redacao.indicadores_texto.num_erros_ortografia += 1

def calcular_indicadores(dados_redacao: Redacao) -> None:
    """
    Calcula os indicados dado o texto de redação de entrada e o prompt da proposta de redação
    """

    _indicadores_spacy(dados_redacao)

    _indicadores_similaridade(dados_redacao)

    _indicadores_language_tool(dados_redacao)

    print(vars(dados_redacao.indicadores_texto))

if __name__ == "__main__":
    # P/ cada redação da pasta redacoes_enem_original

    # dados_redacao: Redacao = buscar_dados_redacao()

    # -- TODO: Iterar sobre cada redação do dataset
    
    id_red = 22

    prompt = "A democratização do acesso ao cinema no Brasil"

    texto_suporte = """
    LC - 1º dia | Caderno 9 - LARANJA - Página 20INSTR UÇÕE S PARA A REDAÇÃO1.
    O rascunho da redação deve ser feito no espaço apropriado. 2.
    O texto definitivo deve ser escrito à tinta preta, na folha própria, em até 30 linhas.3. A redação que apresentar cópia dos textos da Proposta de Redação ou do Caderno de Questões terá o número de linhas copiadas desconsiderado para a contagem de linhas.
    4.
    Receberá nota zero, em qualquer das situações expressas a seguir, a redação que :4.1.
    tiver até 7 (sete) linhas escritas, sendo considerada “texto insuficiente”.4.2.
    fugir ao tema ou que não atender ao tipo dissertativo-argumentativo.4.3.
    apresentar parte do texto deliberadamente desconectada do tema proposto.4.4.
    apresentar nome, assinatura, rubrica ou outras formas de identificação no espaço destinado ao texto.TEXTOS MOTIVADORES

    TEXTO I
    No dia da primeira exibição pública de cinema — 28 de dezembro de 1895, em Paris —, um homem de teatro que trabalhava com mágicas, Georges Mélies, foi falar com Lumière, um dos inventores do cinema; queria adquirir um aparelho, e Lumière desencorajou-o, disse-lhe que o “Cinematógrapho” não tinha o menor futuro como espetáculo, era um instrumento científico para reproduzir o movimento e só poderia servir para pesquisas. Mesmo que o público, no início, se divertisse com ele, seria uma novidade de vida breve, logo cansaria. Lumière enganou-se. Como essa estranha máquina de austeros cientistas virou uma máquina de contar estórias para enormes plateias, de geração em geração, durante já quase um século?

    TEXTO I
    IEdgar Morin define o cinema como uma máquina que registra a existência e a restitui como tal, porém levando em consideração o indivíduo, ou seja, o cinema seria um meio de transpor para a tela o universo pessoal, solicitando a participação do espectador.

    TEXTO I
    IIDescrição da imagem : Infográfico intitulado “Da telona para as telinhas: cresce o percentual de brasileiros que frequentam salas de cinema e o interesse por filmes tem destaque no consumo de TV. ENTENDA!”.
    O infográfico é composto por ícones ilustrativos e dados percentuais.
    As informações são as seguintes:• Nos últimos cinco anos, a penetração do cinema cresceu 43 por cento entre os brasileiros;• 88 por cento dos telespectadores assistem a filmes na TV, regularmente;• 19 por cento dos telespectadores de filmes na TV vão ao cinema;• 17 por cento da população frequenta o cinema, no total (assistiu nos últimos trinta dias);• 95 por cento dos que foram ao cinema assistem a filmes na TV.TEXT O IVO Brasil já teve um parque exibidor vigoroso e desce ntralizado: quase 3 300 salas em 1975, uma para cada 30 000 habitantes, 80% em cidades do interior. Desde então, o país mudou.
    Quase 120 milhões de pessoas a mais passaram a viver nas cidades. A urbanização acelerada, a falta de investimentos em infraestrutura urbana, a baixa capitalização das empresas exibidoras, as mudanças tecnológicas, entre outros fatores, alteraram a geografia do cinema. Em 1997, chegamos a pouco mais de 1 000 salas.
    Com a expansão dos shopping centers, a atividade de exibição se reorganizou. O número de cinemas duplicou, até chegar às atuais 2 200 salas. Esse crescimento, porém, além de insuficiente (o Brasil é apenas o 60º país na relação habitantes por sala), ocorreu de forma concentrada. Foram privilegiadas as áreas de renda mais alta das grandes cidades. Populações inteiras foram excluídas do universo do cinema ou continuam mal atendidas:
    o Norte e o Nordeste, as periferias urbanas, as cidades pequenas e médias do interior."""

    prompt = """
    PROPOSTA DE REDAÇÃO

    A partir da leitura dos textos motivadores e com base nos conhecimentos construídos ao longo de sua formação, redija texto dissertativo-argumentativo em modalidade escrita formal da língua portuguesa sobre o tema
    “Democratização do acesso ao cinema no Brasil”, apresentando proposta de intervenção que respeite os direitos humanos. Selecione, organize e relacione, de forma coerente e coesa, argumentos e fatos para defesa de seu ponto de vista.*LE0175LA20*
    """

    texto_da_redacao = """Embora a Constituição Federal de 1988 assegure o acesso à cultura como direito de todos os cidadãos, percebe-se que, na atual realidade brasileira, não há o cumprimento dessa garantia, principalmente no que diz respeito ao cinema. Isso acontece devido à concentração de salas de cinema nos grandes centros urbanos e à condição cultural de que a arte é direcionada aos mais favorecidos economicamente. É relevante abordar, primeiramente, que as cidades brasileiras foram construídas sob um viés elitista e segregacionista, de modo que os centros culturais estão, em sua maioria, restritos ao espaço ocupado pelos detentores do poder econômico. Essa dinâmica não foi diferente com a chegada do cinema, já que apenas 17% da população do país frequenta os centros culturais em questão. Nesse sentido, observa-se que a segregação social — evidenciada como uma característica da sociedade brasileira, por Sérgio Buarque de Holanda, no livro ""Raízes do Brasil"" — se faz presente até os dias atuais, por privar a população das periferias do acesso à cultura e ao lazer que são proporcionados pelo cinema.
    Paralelo a isso, vale também ressaltar que a concepção cultural de que a arte não abrange a população de baixa renda é um fator limitante para que haja a democratização plena da cultura e, portanto, do cinema. Isso é retratado no livro ""Quarto de Despejo"", de Carolina Maria de Jesus, o qual ilustra o triste cotidiano que uma família em condição de miserabilidade vive, e, assim, mostra como acesso a centros culturais é uma perspectiva distante de sua realidade, não necessariamente pela distância física, mas pela ideia de pertencimento a esses espaços.
    Dessa forma, pode-se perceber que o debate acerca da democratização do cinema é imprescindível para a construção de uma sociedade mais igualitária. Nessa lógica, é imperativo que Ministério da Economia destine verbas para a construção de salas de cinema, de baixo custo ou gratuitas, nas periferias brasileiras por meio da inclusão de seu objetivo na base de Diretrizes Orçamentárias, com o intuito de democratizar o acesso à arte. Além disso, cabe às instituições de ensino promover passeios aos cinemas locais, desde o início da vida escolar das crianças, mediante autorização e contribuição dos responsáveis, a fim de desconstruir a ideia de elitização da cultura, sobretudo em regiões carentes. 
    Feito isso, a sociedade brasileira poderá caminhar para completude da democracia no âmbito cultural.
    """

    notas = [200, 200, 200, 200, 200, 1000]
    
    dados_redacao: Redacao = Redacao(id_red, prompt, texto_suporte, texto_da_redacao, notas, indicadores_texto=None)
    dados_redacao.indicadores_texto = Indicadores(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

    calcular_indicadores(dados_redacao)
    
    # TODO -- Salvar dados em um novo CSV