# Monitor Enjoei para Railway

## Arquivos
- `main.py`: script adaptado para Railway
- `requirements.txt`: dependências Python
- `Dockerfile`: imagem pronta com Playwright

## Variáveis no Railway
Crie estas variables:
- `STATE_FILE=/data/enjoei_state.json`
- `HEADLESS=true`
- `ENVIAR_MENSAGEM_TELEGRAM=true`
- `TELEGRAM_BOT_TOKEN=SEU_TOKEN`
- `TELEGRAM_CHAT_ID=SEU_CHAT_ID`
- `REQUEST_TIMEOUT=30`
- `PAGE_TIMEOUT_MS=60000`
- `WAIT_NETWORK_IDLE_MS=10000`
- `SCROLL_COUNT=3`
- `SCROLL_WAIT_MS=1200`

## Volume
Monte um volume em:
- `/data`

## Cron
Use:
- `*/10 * * * *`
