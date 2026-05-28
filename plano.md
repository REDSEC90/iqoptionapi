# Plano de melhoria iqoptionapi para OB-CC

Data: 2026-05-28
Branch: improve-obcc-checkwin-v4

## Objetivo

Tornar a `iqoptionapi` mais previsivel para uso pelo OB-CC, principalmente nos
fluxos de conexao, envio de ordem, candles e resolucao de resultado.

## Problemas prioritarios

1. `check_win_v4` precisava ler eventos reais de `option-closed`, nao apenas um
   cache legado `socket_option_closed`.
2. Chamadas sem timeout podiam bloquear threads do OB-CC.
3. O websocket armazenava resultado fechado em `order_async`, mas nao no cache
   consultado pelo novo `check_win_v4`.
4. O handler websocket podia deixar o lock global de envio preso se uma excecao
   escapasse antes do final.
5. `get-candles` enviava uma chave vazia no payload.
6. Varias rotinas ainda usam busy-wait, estado global e dados compartilhados.

## Fase 1 - Resultado OB-CC

Status: implementado parcialmente nesta branch.

- Normalizar payloads `option-closed` e `socket-option-closed`.
- Fazer `check_win_v4` consultar `socket_option_closed` e `order_async`.
- Calcular lucro pelos schemas `profit_amount - amount` e
  `win_amount - sum`.
- Usar timeout finito por padrao para evitar bloqueio no OB-CC.
- Cobrir o fluxo real `option-closed` em teste unitario.
- Armazenar eventos fechados no cache consultado pelo OB-CC.
- Reduzir busy-wait em compra, candles e handshake websocket.
- Cobrir cache websocket de `option-closed` em teste unitario.

## Fase 2 - Timeouts e busy-wait

Status: implementado parcialmente nesta branch.

- Corrigir loops `pass` em `connect`, `send_ssid`, `get_candles`, `buy`,
  `get_order` e rotinas digitais.
- Trocar spin loops por `threading.Event`, `Condition` ou sleep curto.
- Adicionar timeout parametrizavel nas operacoes publicas.
- Corrigir `while self.check_connect` para chamada real do metodo.
- Adicionar timeout em `get_betinfo`, `get_order`, `get_pending`,
  `get_positions`, `get_position`, `buy_multi`, `buy_digital_spot` e
  `close_digital_option`.
- Corrigir `start_mood_stream`/`stop_mood_stream` para nao usar comparacao
  encadeada incorreta, nao indexar lista com string e respeitar timeout.
- Tornar `stop_candles_stream`, `stop_candles_one_stream` e
  `stop_candles_all_size_stream` limitados por timeout e com retorno
  booleano consistente.
- Tornar `buy_digital`, `buy_digital_spot` e `close_digital_option`
  diagnosticaveis via `last_operation`, com timeout parametrizavel e sem
  busy-wait puro.
- Tornar `get_optioninfo`, `get_optioninfo_v2`, `sell_option` e
  `get_strike_list` limitados por timeout, com `sleep` curto e diagnostico.
- Tornar consultas digitais e de portfolio (`get_digital_position`,
  `get_position_history`, `get_available_leverages`, `cancel_order`,
  `close_position`, `get_overnight_fee`) limitadas por timeout e observaveis
  via `last_operation`.
- Tornar `buy_order`, `change_auto_margin_call` e `change_order` limitados por
  timeout, com diagnostico de aceite, rejeicao e pendencia.
- Tornar resultados legados (`check_win`, `check_win_v2`, `check_win_v3`)
  limitados por timeout e consistentes com o calculo normalizado de lucro.
- Tornar `get_financial_information` limitado por timeout e observavel via
  `last_operation`.

## Fase 3 - Estado por instancia

Status: iniciado nesta branch.

- Mover atributos mutaveis de classe para `__init__`.
- Reduzir dependencia de `global_value`.
- Criar locks por instancia para websocket, ordens, candles e resultados.
- Usar `request_id` unico por operacao.
- Inicializar caches mutaveis de resultado, candles, ordens, perfil e dados de
  websocket por instancia de `IQOptionAPI`.
- Tornar `close()` e `websocket_alive()` seguros antes ou apos falha parcial de
  conexao.
- Serializar envios websocket por instancia com lock local, mantendo flags
  globais apenas como compatibilidade legada.

## Fase 4 - Compra e candles

Status: iniciado nesta branch.

- Padronizar retorno de compra com `accepted`, `order_id`, `reason` e `raw`.
- Separar rejeicao de broker de falha de transporte.
- Normalizar candles para `from`, `open`, `max`, `min`, `close`, `volume`.
- Garantir ordenacao e validacao de timeframe/count.
- Corrigir expiração para depender do timestamp do broker de forma consistente.
- Gerar `request_id` unico para `buy` e `buy_by_raw_expirations` mantendo o
  contrato publico atual.
- Validar ativo/timeframe/count antes de enviar `get-candles`.
- Normalizar candles preservando payload original e garantindo aliases
  `high`/`low`, `max`/`min` e `volume`.
- Cobrir fluxo offline `buy -> option-closed -> check_win_v4`, sem broker real,
  para proteger o contrato usado pelo OB-CC.

## Fase 5 - Observabilidade

Status: iniciado nesta branch.

- Emitir eventos estruturados de conexao, compra, rejeicao, candle, resultado,
  timeout e reconnect.
- Incluir latencia, `request_id`, `order_id` e motivo classificado.
- Preservar dados sensiveis fora de logs.
- Expor `last_operation` com nome, status, motivo, payload resumido e timestamp
  para diagnostico simples de chamadas publicas.
- Propagar `request_id` em `get-candles` e registrar esse identificador em
  `last_operation`.
- Registrar erro de processamento websocket em `websocket_last_message_error`
  sem deixar mensagem malformada prender mutex ou derrubar o handler.
- Registrar payloads `option-closed` malformados em
  `closed_option_last_error`, sem quebrar o cache de resultados validos.
- Expor `get_api_diagnostics()` no wrapper publico `stable_api` para o OB-CC
  consumir `last_operation` e erros de transporte sem depender de atributos
  internos.

## Fase 6 - Testes e gates

- Unitarios sem broker para eventos websocket, candles, compra rejeitada e
  timeouts.
- Contratos com wrapper OB-CC.
- Smoke PRACTICE somente por opt-in, com limite de tempo e uma ordem pequena.

## Criterios de aceite para OB-CC

- `check_win_v4(order_id)` nunca trava indefinidamente por padrao.
- Ordem fechada por `option-closed` retorna `win`, `loss` ou `draw` corretamente.
- Resultado pendente retorna `(False, None)` dentro do timeout.
- `get_candles` nao envia payload invalido.
- Falhas de websocket nao deixam o envio travado.
