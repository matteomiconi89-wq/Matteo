# VOCI NON DISPONIBILI - FILIERA UN CLIC V2
#
# Nessun motore di sintesi vocale ha funzionato in questo ambiente remoto:
# la rete in uscita e' governata dal proxy dell'ambiente, che blocca gli
# endpoint dei servizi TTS. Errori esatti registrati il 2026-09-03:
#
# 1) edge-tts 7.2.8, voce "it-IT-DiegoNeural", rate "+6%"
#    Primo tentativo (prima della correzione del CA bundle del proxy):
#      aiohttp.client_exceptions.ClientConnectorCertificateError:
#      Cannot connect to host speech.platform.bing.com:443 ssl:True
#      [SSLCertVerificationError: (1, '[SSL: CERTIFICATE_VERIFY_FAILED]
#      certificate verify failed: self-signed certificate in certificate
#      chain (_ssl.c:1016)')]
#    Dopo aver aggiunto /root/.ccr/ca-bundle.crt allo store di certifi
#    (due tentativi, entrambi identici):
#      aiohttp.client_exceptions.WSServerHandshakeError: 403,
#      message='Invalid response status',
#      url='wss://speech.platform.bing.com/consumer/speech/synthesize/
#           readaloud/edge/v1?TrustedClientToken=...&Sec-MS-GEC=...'
#
# 2) gTTS 2.5.4, lang='it'
#      gtts.tts.gTTSError: Failed to connect. Probable cause: Unknown
#    Causa sottostante verificata con requests verso
#    https://translate.google.com/_/TranslateWebserverUi/data/batchexecute :
#      requests.exceptions.ProxyError: HTTPSConnectionPool(
#      host='translate.google.com', port=443): Max retries exceeded
#      (Caused by ProxyError('Unable to connect to proxy',
#      OSError('Tunnel connection failed: 403 Forbidden')))
#
# Conclusione: il proxy dell'ambiente rifiuta il tunnel verso
# speech.platform.bing.com e translate.google.com (403 Forbidden),
# quindi ne' edge-tts ne' gTTS possono raggiungere i rispettivi servizi.
# Le 11 voci (voce01.mp3 .. voce11.mp3) vanno generate da un ambiente con
# accesso di rete a uno dei due servizi, oppure con un TTS offline.
