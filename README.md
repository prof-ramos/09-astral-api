# Astrologer API

A Astrologer API é um serviço independente que fornece cálculos astrológicos extensivos, projetado para integração perfeita em projetos. Ela oferece um conjunto completo de mapas astrológicos e dados, tornando-se uma ferramenta inestimável tanto para desenvolvedores quanto para entusiastas da astrologia. A API foi refatorada de sua versão original RapidAPI para ser um serviço autônomo e escalável com autenticação moderna.

Aqui está um exemplo de mapa natal gerado usando a Astrologer API:

![Mapa de John Lennon](https://raw.githubusercontent.com/g-battaglia/kerykeion/refs/heads/master/tests/charts/svg/John%20Lennon%20-%20Dark%20Theme%20-%20Natal%20Chart.svg)


## Visão Geral Rápida dos Endpoints


| Endpoint                          | Método | Descrição |
|-----------------------------------|--------|-----------|
| `/api/v4/birth-chart`            | POST   | Gera um mapa natal completo como string SVG, incluindo posições planetárias e aspectos. |
| `/api/v4/synastry-chart`         | POST   | Cria um mapa de sinastria comparando dois sujeitos, exibindo suas interações e compatibilidade, junto com uma representação SVG. |
| `/api/v4/transit-chart`          | POST   | Gera um mapa de trânsito para um sujeito, mostrando influências planetárias atuais, com representação visual SVG. |
| `/api/v4/composite-chart`        | POST   | Computa um mapa composto para dois sujeitos usando o método do ponto médio, incluindo aspectos e representação visual SVG. |
| `/api/v4/relationship-score`     | POST   | Calcula uma pontuação de compatibilidade (0-44) usando o método Ciro Discepolo para avaliar o potencial de relacionamento. |
| `/api/v4/natal-aspects-data`     | POST   | Fornece dados detalhados do mapa natal e aspectos sem o mapa visual. |
| `/api/v4/synastry-aspects-data`  | POST   | Retorna dados relacionados à sinastria e aspectos entre dois sujeitos, sem mapa SVG. |
| `/api/v4/transit-aspects-data`   | POST   | Oferece dados do mapa de trânsito e aspectos para um sujeito, sem representação visual SVG. |
| `/api/v4/composite-aspects-data` | POST   | Entrega dados do mapa composto e aspectos sem gerar mapa SVG. |
| `/api/v4/birth-data`             | POST   | Retorna dados essenciais do mapa natal sem aspectos ou representação visual. |
| `/api/v4/now`                    | GET    | Obtém dados do mapa natal para a hora UTC atual, excluindo aspectos e o mapa visual. |

## Acesso à API

A Astrologer API está disponível como um serviço independente com autenticação por chave de API. Este serviço foi projetado especificamente para os padrões astrológicos brasileiros.

## Documentação

Explore a documentação abrangente da API:

- **Especificação da API**: Consulte a documentação técnica incluída no projeto
- **Documentação Interativa**: Acesse `/docs` quando o servidor estiver rodando para ver a documentação Swagger
- **Redoc**: Acesse `/redoc` para uma versão alternativa da documentação

## Instalação e Desenvolvimento

### Requisitos
- Python 3.11+
- Pipenv ou UV para gerenciamento de dependências

### Configuração Local

1. **Clone o repositório:**
```bash
git clone https://github.com/g-battaglia/v4.astrologer-api.git
cd v4.astrologer-api
```

2. **Instale as dependências:**
```bash
# Usando Pipenv (recomendado)
pipenv install && pipenv install --dev

# Ou usando UV (mais rápido)
uv venv && source .venv/bin/activate
uv pip install -r <(pipenv requirements)
uv pip install tomli  # Para Python < 3.11
```

3. **Configure as variáveis de ambiente:**
```bash
export ALLOWED_API_KEYS="test-key-123,dev-key-456"
export GEONAMES_USERNAME="seu_usuario_geonames"  # Opcional
export ENV_TYPE="dev"
```

4. **Execute o servidor de desenvolvimento:**
```bash
pipenv run dev
# ou
uvicorn app.main:app --reload
```

A API estará disponível em `http://localhost:8000` com documentação em `/docs`.

### Comandos de Desenvolvimento

```bash
# Executar testes
pipenv run test

# Verificação de tipos
pipenv run quality

# Formatação de código
pipenv run format

# Gerar esquema OpenAPI
pipenv run schema
```

### Testando a API

```bash
# Endpoint público (sem autenticação)
curl http://localhost:8000/
curl http://localhost:8000/api/v4/health

# Endpoint protegido (com chave de API)
curl -H "X-API-Key: test-key-123" http://localhost:8000/api/v4/now
```

## Primeiros Passos

Para começar a usar a Astrologer API, você precisa incluir sua chave de API nos cabeçalhos da requisição.

### Autenticação

Todos os endpoints da API (exceto verificações de saúde) requerem autenticação via chave de API nos cabeçalhos da requisição.

### Exemplo de Cabeçalhos de Requisição

Certifique-se de que suas requisições de API incluam o seguinte cabeçalho:

```javascript
headers: {
    'X-API-Key': 'SUA_CHAVE_API'
}
```

Substitua `SUA_CHAVE_API` pela sua chave de API real fornecida pelo administrador da API.

### Configuração do Ambiente

Configure as seguintes variáveis de ambiente:

```bash
# Obrigatório para autenticação da API
ALLOWED_API_KEYS="sua_chave_api_1,sua_chave_api_2,sua_chave_api_3"

# Opcional: Para resolução automática de coordenadas (recomendado)
GEONAMES_USERNAME="seu_usuario_geonames"

# Opcional: Definir tipo de ambiente
ENV_TYPE="dev"  # ou "production"

# Padrão: Idioma brasileiro
DEFAULT_LANGUAGE="PT"

# Padrão: Fuso horário São Paulo
DEFAULT_TIMEZONE="America/Sao_Paulo"
```


## Funcionalidades

**Padrões Brasileiros:** Esta API foi desenvolvida especificamente para os padrões astrológicos brasileiros, com idioma português como padrão, fuso horário de São Paulo (America/Sao_Paulo), zodíaco tropical, sistema de casas Placidus e perspectiva geocêntrica aparente. Todos os exemplos e configurações padrão seguem estes critérios nacionais.

### Mapas

A Astrologer API fornece vários endpoints `*-chart` com opções personalizáveis:

#### Idiomas

Você pode especificar o parâmetro `lang` para selecionar o idioma do seu mapa. As opções disponíveis são:

- `PT`: Português (padrão)
- `EN`: Inglês
- `FR`: Francês
- `ES`: Espanhol
- `TR`: Turco
- `RU`: Russo
- `IT`: Italiano
- `CN`: Chinês
- `DE`: Alemão
- `HI`: Hindi

Exemplo de requisição da API:

```json
{
    "subject": {
        "year": 1980,
        "month": 12,
        "day": 12,
        "hour": 12,
        "minute": 12,
        "longitude": -46.633308,
        "latitude": -23.550520,
        "city": "São Paulo",
        "nation": "BR",
        "timezone": "America/Sao_Paulo",
        "name": "João Silva",
        "zodiac_type": "Tropic"
    },
    "language": "PT"
}
```

#### Temas

Personalize a aparência dos seus mapas usando o parâmetro `theme`. Os temas disponíveis são:

Temas disponíveis:

- `light`: Tema claro moderno com cores suaves

![Exemplo de Mapa de John Lennon](https://raw.githubusercontent.com/g-battaglia/kerykeion/refs/heads/master/tests/charts/svg/John%20Lennon%20-%20Light%20Theme%20-%20Natal%20Chart.svg)

- `dark`: Tema escuro moderno

![Exemplo de Mapa de John Lennon](https://raw.githubusercontent.com/g-battaglia/kerykeion/refs/heads/master/tests/charts/svg/John%20Lennon%20-%20Dark%20Theme%20-%20Natal%20Chart.svg)

- `dark-high-contrast`: Tema escuro de alto contraste

![Exemplo de Mapa de John Lennon](https://raw.githubusercontent.com/g-battaglia/kerykeion/refs/heads/master/tests/charts/svg/John%20Lennon%20-%20Dark%20High%20Contrast%20Theme%20-%20Natal%20Chart.svg)

- `classic`: Tema colorido tradicional

![Exemplo de Mapa de Albert Einstein](https://raw.githubusercontent.com/g-battaglia/kerykeion/refs/heads/master/tests/charts/svg/Albert%20Einstein%20-%20Natal%20Chart.svg)

Exemplo de requisição da API:

```json
{
    "subject": {
        "year": 1980,
        "month": 12,
        "day": 12,
        "hour": 12,
        "minute": 12,
        "longitude": -46.633308,
        "latitude": -23.550520,
        "city": "São Paulo",
        "nation": "BR",
        "timezone": "America/Sao_Paulo",
        "name": "João Silva",
        "zodiac_type": "Tropic"
    },
    "theme": "dark"
}
```


### Tipos de Zodíaco

Você pode escolher entre os zodíacos Sideral e Tropical usando o parâmetro `zodiac_type` na chave `subject` da maioria dos endpoints.

- `tropic`: Zodíaco tropical (padrão no Brasil)
- `sidereal`: Zodíaco sideral

Se você selecionar `sidereal`, deve também especificar o parâmetro `sidereal_mode`, que oferece vários ayanamshas (modos de cálculo zodiacal):

- `FAGAN_BRADLEY`
- `LAHIRI` (padrão para astrologia védica)
- `DELUCE`
- `RAMAN`
- `USHASHASHI`
- `KRISHNAMURTI`
- `DJWHAL_KHUL`
- `YUKTESHWAR`
- `JN_BHASIN`
- `BABYL_KUGLER1`
- `BABYL_KUGLER2`
- `BABYL_KUGLER3`
- `BABYL_HUBER`
- `BABYL_ETPSC`
- `ALDEBARAN_15TAU`
- `HIPPARCHOS`
- `SASSANIAN`
- `J2000`
- `J1900`
- `B1950`

Os ayanamshas mais comumente usados são `FAGAN_BRADLEY` e `LAHIRI`.

Exemplo de requisição da API:

```json
{
    "subject": {
        "year": 1980,
        "month": 12,
        "day": 12,
        "hour": 12,
        "minute": 12,
        "longitude": -46.633308,
        "latitude": -23.550520,
        "city": "São Paulo",
        "nation": "BR",
        "timezone": "America/Sao_Paulo",
        "name": "João Silva",
        "zodiac_type": "Sidereal",
        "sidereal_mode": "FAGAN_BRADLEY"
    }
}
```

### Sistemas de Casas

O parâmetro `HouseSystem` define o método usado para dividir a esfera celestial em doze casas. Aqui estão as opções disponíveis:

- **A**: Igual
- **B**: Alcabitius
- **C**: Campanus
- **D**: Igual (MC)
- **F**: Carter poli-equ.
- **H**: Horizonte/Azimute
- **I**: Sunshine
- **i**: Sunshine/Alt.
- **K**: Koch
- **L**: Pullen SD
- **M**: Morinus
- **N**: Igual/1=Áries
- **O**: Porphyry
- **P**: Placidus
- **Q**: Pullen SR
- **R**: Regiomontanus
- **S**: Sripati
- **T**: Polich/Page
- **U**: Krusinski-Pisa-Goelzer
- **V**: Igual/Vehlow
- **W**: Igual/Signo Inteiro
- **X**: Sistema de rotação axial/Casas meridionais
- **Y**: Casas APC

Geralmente, o sistema de casas padrão usado no Brasil é Placidus (P).

Exemplo de requisição da API:

```json
{
    "subject": {
        "year": 1980,
        "month": 12,
        "day": 12,
        "hour": 12,
        "minute": 12,
        "longitude": -46.633308,
        "latitude": -23.550520,
        "city": "São Paulo",
        "nation": "BR",
        "timezone": "America/Sao_Paulo",
        "name": "João Silva",
        "zodiac_type": "Tropic",
        "house_system": "A"
    }
}
```

Isso permite especificar o sistema de casas desejado para calcular e exibir as posições dos corpos celestes.

### Tipos de Perspectiva

O PerspectiveType define o ponto de vista a partir do qual as posições dos corpos celestes são calculadas. Aqui estão as opções disponíveis:

- "Apparent Geocentric": Centrado na Terra e mostra as posições aparentes dos corpos celestes como vistos da Terra. Esta é a mais comumente usada e a perspectiva padrão no Brasil.
- "Heliocentric": Centrado no Sol.
- "Topocentric": Esta perspectiva é baseada na localização específica do observador na superfície da Terra.
- "True Geocentric": Esta perspectiva também é centrada na Terra, mas mostra as posições verdadeiras dos corpos celestes sem os desvios aparentes causados pela atmosfera da Terra.

Geralmente, a perspectiva padrão usada no Brasil é "Apparent Geocentric".

Exemplo de uso em uma requisição da API:

```json
{
    "subject": {
        "year": 1980,
        "month": 12,
        "day": 12,
        "hour": 12,
        "minute": 12,
        "longitude": -46.633308,
        "latitude": -23.550520,
        "city": "São Paulo",
        "nation": "BR",
        "timezone": "America/Sao_Paulo",
        "name": "João Silva",
        "zodiac_type": "Tropic",
        "perspective": "Heliocentric"
    }
}
```

Isso permite especificar a perspectiva desejada para calcular e exibir as posições dos corpos celestes.

### Mapas Apenas com Roda

Para gerar mapas que contenham apenas a roda zodiacal sem qualquer informação textual, você pode usar a opção `wheel_only` na sua chamada da API. Quando esta opção é definida como `True`, apenas a roda zodiacal será retornada.

Exemplo de requisição da API:

```json
{
    "subject": {
        "year": 1980,
        "month": 12,
        "day": 12,
        "hour": 12,
        "minute": 12,
        "longitude": -46.633308,
        "latitude": -23.550520,
        "city": "São Paulo",
        "nation": "BR",
        "timezone": "America/Sao_Paulo",
        "name": "João Silva",
        "zodiac_type": "Tropic"
    },
    "wheel_only": true
}
```

Isso pode ser útil para criar representações visuais limpas e simples do zodíaco sem qualquer desordem adicional.

## Fuso Horários

Cálculos astrológicos precisos requerem o fuso horário correto. Consulte o seguinte link para uma lista completa de fusos horários:

[Lista de Fusos Horários do Banco de Dados TZ](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)

#### Pontos Ativos e Aspectos

Para todos os endpoints de Mapas (Mapa Natal, Mapa de Trânsito),
Dados de Aspectos Natals e Dados de Aspectos de Sinastria você pode personalizar quais pontos celestes incluir e quais aspectos calcular usando os parâmetros `active_points` e `active_aspects`.

Exemplo de requisição da API:

```json
{
    "subject": {
        "year": 1980,
        "month": 12,
        "day": 12,
        "hour": 12,
        "minute": 12,
        "longitude": -46.633308,
        "latitude": -23.550520,
        "city": "São Paulo",
        "nation": "BR",
        "timezone": "America/Sao_Paulo",
        "name": "João Silva",
        "zodiac_type": "Tropic"
    },
    "active_points": [
        "Sun",
        "Moon",
        "Mercury",
        "Venus",
        "Mars",
        "Jupiter",
        "Saturn",
        "Uranus",
        "Neptune",
        "Pluto",
        "Mean_Node",
        "Chiron",
        "Ascendant",
        "Medium_Coeli",
        "Mean_Lilith",
        "Mean_South_Node"
    ],
    "active_aspects": [
        {
            "name": "conjunction",
            "orb": 10
        },
        {
            "name": "opposition",
            "orb": 10
        },
        {
            "name": "trine",
            "orb": 8
        },
        {
            "name": "sextile",
            "orb": 6
        },
        {
            "name": "square",
            "orb": 5
        },
        {
            "name": "quintile",
            "orb": 1
        }
    ]
}
```

Estes parâmetros permitem:
- Especificar quais pontos celestes incluir no mapa e cálculos
- Definir quais aspectos calcular junto com seus orbes (o grau de desvio permitido do aspecto exato)

## Coordenadas Automáticas

É possível usar coordenadas automáticas se você não quiser implementar um método diferente para calcular latitude, longitude e fuso horário.

Para fazer isso, você deve passar o parâmetro `geonames_username` dentro do objeto `subject` em todas as requisições que contenham o objeto `subject`.

**Lógica**

- Se `geonames_username` estiver presente, os parâmetros `longitude`, `latitude` e `timezone` são automaticamente ignorados.
- Se **NÃO** estiver presente, todos os três parâmetros (`longitude`, `latitude` e `timezone`) devem ser especificados.

**Recomendação**

É recomendado usar coordenadas reais diretamente para maior precisão.

**Obtendo um Nome de Usuário Geonames**

Se você quiser calcular coordenadas automaticamente, precisa obter um `username` para o serviço de Fuso Horário Geonames. O serviço é gratuito para até **10.000 requisições por dia**.
Você pode obter um nome de usuário Geonames cadastrando-se em <a href="http://www.geonames.org/login" target="_blank">Geonames</a>.

**Exemplo**

```json
{
    "subject": {
        "year": 1980,
        "month": 12,
        "day": 12,
        "hour": 12,
        "minute": 12,
        "city": "São Paulo, SP",
        "nation": "BR",
        "name": "João Silva",
        "zodiac_type": "Tropic",
        "geonames_username": "SEU_USUARIO_GEONAMES"
    }
}
```

## Direitos Autorais e Licença

A Astrologer API é um Software Livre/Open Source com licença AGPLv3. Todos os termos e condições da licença AGPLv3 se aplicam à Astrologer API.
Você pode revisar e contribuir com o código fonte através dos repositórios oficiais:

- [V4 Astrologer API](https://github.com/g-battaglia/v4.astrologer-api)

A Astrologer API é desenvolvida por Giacomo Battaglia e é baseada no Kerykeion, uma biblioteca Python para cálculos astrológicos do mesmo autor. As ferramentas subjacentes são construídas sobre o Swiss Ephemeris.

Como é um serviço de API externo, integrar dados e mapas obtidos via API não impõe restrições de licenciamento, permitindo uso em projetos com licenças de código fechado.

## Uso Comercial

A Astrologer API pode ser livremente usada em aplicações comerciais open-source e closed-source sem restrições, pois funciona como um serviço externo.

Para conformidade total, recomendamos adicionar esta declaração nos seus Termos e Condições ou em outro lugar no seu site/app:

---
Dados astrológicos e mapas neste site são gerados usando a Astrologer API, um serviço open-source licenciado sob AGPL v3. Código fonte:
- [V4 Astrologer API](https://github.com/g-battaglia/v4.astrologer-api)
- [Astrologer API Original](https://github.com/g-battaglia/Astrologer-API)
---

Isso garante transparência total e conformidade completa de licenciamento, não deixando espaço para dúvidas.


## Contato e Suporte

Precisa de ajuda ou tem feedback? Entre em contato conosco:
[kerykeion.astrology@gmail.com](mailto:kerykeion.astrology@gmail.com)  
