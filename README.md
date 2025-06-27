# Leitor de Notas Fiscais

Este projeto permite que você faça perguntas sobre notas fiscais a partir de arquivos CSV, utilizando agentes de IA com LangChain e Streamlit.

## Como rodar o projeto

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/luisramosbh/alphaagents.git
   cd alphaagents
   ```

2. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure sua chave da OpenAI:**
   - Crie um arquivo chamado `.env` na raiz do projeto com o seguinte conteúdo:
     ```
     OPENAI_API_KEY=sua_chave_aqui
     ```
   - Substitua `sua_chave_aqui` pela sua chave pessoal da OpenAI, que pode ser obtida em https://platform.openai.com/api-keys

4. **Execute o sistema:**
   ```bash
   streamlit run questionariov6.py
   ```

5. **Faça perguntas na interface web!**

## Exemplo de perguntas
- Qual o valor total das notas emitidas?
- Qual fornecedor recebeu o maior montante?
- Qual item teve maior volume entregue?
- Qual a UF com maior número de notas?

## Observações
- O arquivo `.env` **não está no repositório** por segurança. Siga as instruções acima para criar o seu.
- (Opcional) Você pode usar o arquivo `.env.example` como base.

## Dependências principais
- Python 3.8+
- Streamlit
- LangChain
- OpenAI
- Pandas
- python-dotenv

---

**Dúvidas?** Abra uma issue no repositório ou entre em contato!
