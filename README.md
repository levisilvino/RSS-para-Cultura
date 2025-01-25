# RSS para Cultura

Um agregador de feeds RSS focado em oportunidades culturais, como editais, prêmios e concursos na área da cultura.

## Funcionalidades

- Agregação de feeds RSS de diversas fontes culturais
- Extração automática de datas e categorias dos editais
- Interface web moderna e responsiva
- Filtros por categoria, data e texto
- Gerenciamento de fontes RSS

## Tecnologias Utilizadas

### Backend
- Python 3.8+
- Flask (Framework web)
- SQLAlchemy (ORM)
- APScheduler (Agendamento de tarefas)
- BeautifulSoup4 (Web scraping)
- Feedparser (Parsing RSS)

### Frontend
- React 18
- TypeScript
- Tailwind CSS
- Vite
- Axios

## Instalação

### Backend

1. Crie um ambiente virtual Python:
```bash
python -m venv venv
```

2. Ative o ambiente virtual:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Instale as dependências:
```bash
cd backend
pip install -r requirements.txt
```

4. Execute o servidor:
```bash
flask run
```

### Frontend

1. Instale as dependências:
```bash
npm install
```

2. Execute o servidor de desenvolvimento:
```bash
npm run dev
```

## Uso

1. Acesse o frontend em `http://localhost:3000`
2. Use o gerenciador de fontes para adicionar feeds RSS culturais
3. O sistema irá automaticamente buscar e categorizar os editais
4. Use os filtros para encontrar oportunidades específicas

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.
