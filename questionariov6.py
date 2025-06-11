import streamlit as st
import pandas as pd
import zipfile
import os
from datetime import datetime
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import json

# Configuracao
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@st.cache_data
def carregar_dados_nf(zip_path):
    """Carrega os dados das notas fiscais do arquivo ZIP"""
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            df_cab = pd.read_csv(z.open("202401_NFs_Cabecalho.csv"))
            df_itens = pd.read_csv(z.open("202401_NFs_Itens.csv"))
        
        if 'DATA EMISSAO' in df_cab.columns:
            df_cab['DATA EMISSAO'] = pd.to_datetime(df_cab['DATA EMISSAO'], errors='coerce')
        if 'DATA EMISSAO' in df_itens.columns:
            df_itens['DATA EMISSAO'] = pd.to_datetime(df_itens['DATA EMISSAO'], errors='coerce')
            
        return df_cab, df_itens
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None, None

def obter_resumo_dados(df_cab, df_itens):
    """Gera resumo dos dados para contexto"""
    resumo = {
        "total_notas": len(df_cab),
        "total_itens": len(df_itens),
        "valor_total": df_cab['VALOR NOTA FISCAL'].sum() if 'VALOR NOTA FISCAL' in df_cab.columns else 0,
        "periodo_inicio": df_cab['DATA EMISSAO'].min().strftime('%Y-%m-%d') if 'DATA EMISSAO' in df_cab.columns else "N/A",
        "periodo_fim": df_cab['DATA EMISSAO'].max().strftime('%Y-%m-%d') if 'DATA EMISSAO' in df_cab.columns else "N/A",
        "ufs": df_cab['UF EMITENTE'].unique().tolist() if 'UF EMITENTE' in df_cab.columns else []
    }
    return resumo

def criar_agente_especialista():
    """Cria o agente especialista em analise de notas fiscais"""
    
    template = """
    Voce e um especialista em analise de notas fiscais brasileiras.
    
    Dados disponiveis:
    - Cabecalho das Notas (df_cab): CHAVE DE ACESSO, NUMERO, DATA EMISSAO, RAZAO SOCIAL EMITENTE, UF EMITENTE, VALOR NOTA FISCAL, etc.
    - Itens das Notas (df_itens): DESCRICAO DO PRODUTO/SERVICO, QUANTIDADE, VALOR UNITARIO, VALOR TOTAL, CFOP, NCM, etc.
    
    Contexto dos dados: {resumo_dados}
    
    Pergunta: {pergunta}
    
    Responda de forma clara e objetiva com os dados disponiveis. Use numeros formatados (R$ para valores).
    """
    
    prompt = PromptTemplate(
        input_variables=["resumo_dados", "pergunta"],
        template=template
    )
    
    llm = ChatOpenAI(
        model_name="gpt-4o-mini",
        temperature=0.1,
        openai_api_key=OPENAI_API_KEY
    )
    
    return LLMChain(llm=llm, prompt=prompt)

def criar_agente_revisor():
    """Cria o agente revisor para validar as respostas"""
    
    template = """
    Voce e um revisor especializado em validar respostas sobre notas fiscais.
    
    Pergunta original: {pergunta}
    Resposta do especialista: {resposta_especialista}
    Contexto dos dados: {resumo_dados}
    
    Sua tarefa:
    1. Verificar se a resposta esta correta e coerente
    2. Corrigir erros se houver
    3. Melhorar a clareza se necessario
    4. Manter o formato e valores apresentados
    
    Forneca a resposta final revisada:
    """
    
    prompt = PromptTemplate(
        input_variables=["pergunta", "resposta_especialista", "resumo_dados"],
        template=template
    )
    
    llm = ChatOpenAI(
        model_name="gpt-4o-mini",
        temperature=0.1,
        openai_api_key=OPENAI_API_KEY
    )
    
    return LLMChain(llm=llm, prompt=prompt)

def processar_pergunta(pergunta, resumo_dados):
    """Processa a pergunta usando os dois agentes"""
    
    # Preparar resumo como string
    resumo_str = f"""
    Total de Notas: {resumo_dados['total_notas']:,}
    Total de Itens: {resumo_dados['total_itens']:,}
    Valor Total: R$ {resumo_dados['valor_total']:,.2f}
    Periodo: {resumo_dados['periodo_inicio']} a {resumo_dados['periodo_fim']}
    UFs: {', '.join(resumo_dados['ufs'][:5])}
    """
    
    try:
        # Agente Especialista
        especialista = criar_agente_especialista()
        resposta_inicial = especialista.run(
            resumo_dados=resumo_str,
            pergunta=pergunta
        )
        
        # Agente Revisor
        revisor = criar_agente_revisor()
        resposta_final = revisor.run(
            pergunta=pergunta,
            resposta_especialista=resposta_inicial,
            resumo_dados=resumo_str
        )
        
        return resposta_final
        
    except Exception as e:
        return f"Erro ao processar pergunta: {str(e)}"

def main():
    st.set_page_config(
        page_title="Analise de Notas Fiscais",
        page_icon="📊",
        layout="centered"
    )
    
    st.title("📊 Analise de Notas Fiscais")
    st.markdown("---")
    
    # Verificar arquivo
    zip_file = "202401_NFs.zip"
    if not os.path.exists(zip_file):
        st.error("Arquivo de dados nao encontrado!")
        return
    
    # Carregar dados
    if 'dados_carregados' not in st.session_state:
        with st.spinner("Carregando dados..."):
            df_cab, df_itens = carregar_dados_nf(zip_file)
            if df_cab is not None and df_itens is not None:
                st.session_state.dados_carregados = True
                st.session_state.resumo_dados = obter_resumo_dados(df_cab, df_itens)
            else:
                st.error("Erro ao carregar dados!")
                return
    
    # Interface principal
    pergunta = st.text_area(
        "Digite sua pergunta sobre as notas fiscais:",
        placeholder="Ex: Qual o valor total das notas emitidas?",
        height=100
    )
    
    if st.button("Analisar", type="primary", use_container_width=True):
        if pergunta.strip():
            with st.spinner("Processando..."):
                resposta = processar_pergunta(pergunta, st.session_state.resumo_dados)
                
                st.markdown("### Resposta")
                st.write(resposta)
        else:
            st.warning("Por favor, digite uma pergunta!")

if __name__ == "__main__":
    main()