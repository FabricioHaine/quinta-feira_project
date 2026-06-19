# Quinta-Feira Mobile

Assistente IA pessoal para Android, criada pelo FebrasHz e Leonardo Neto.

## Pré-requisitos

1. **Flutter SDK** - https://docs.flutter.dev/get-started/install/windows/mobile
2. **Android Studio** - https://developer.android.com/studio
3. **Celular Android** com modo desenvolvedor ativado

## Instalação

### 1. Instalar Flutter

```bash
# Baixe e extraia o Flutter em C:\flutter
# Adicione C:\flutter\bin ao PATH do sistema

# Verifique a instalação
flutter doctor
```

### 2. Configurar Android Studio

1. Instale o Android Studio
2. Abra e vá em Tools > SDK Manager
3. Instale Android SDK (API 33 ou superior)
4. Instale o plugin Flutter no Android Studio

### 3. Preparar o Celular

1. Ative o **Modo Desenvolvedor** nas configurações
2. Ative **Depuração USB**
3. Conecte o celular no PC via USB
4. Aceite a depuração quando aparecer no celular

### 4. Rodar o App

```bash
# Entre na pasta do projeto
cd D:\quinta-feira_project\quinta_feira_mobile

# Instale as dependências
flutter pub get

# Execute no celular
flutter run
```

### 5. Gerar APK (para instalar sem PC)

```bash
# Gere o APK de release
flutter build apk

# O APK estará em: build/app/outputs/flutter-apk/app-release.apk
# Copie para o celular e instale
```

## Funcionalidades

- Reconhecimento de voz em português
- Respostas por áudio com voz natural
- Integração com Gemini API
- Interface estilo FRIDAY
- Histórico de conversas
- Personalidade: Fébras H Z e Leonardo Neto

## Comandos de Voz

- "Quinta, quem te criou?"
- "Quinta, que horas são?"
- "Quinta, me conte uma piada"
- Qualquer pergunta ou comando

## Estrutura do Projeto

```
quinta_feira_mobile/
├── lib/
│   ├── main.dart
│   ├── screens/
│   │   └── home_screen.dart
│   └── services/
│       ├── speech_service.dart
│       └── ai_service.dart
├── android/
│   └── app/
│       └── src/
│           └── main/
│               └── AndroidManifest.xml
└── pubspec.yaml
```

## Solução de Problemas

- **Áudio não funciona**: Verifique as permissões de microfone
- **Reconhecimento falha**: Fale claro e em ambiente silencioso
- **Erro de conexão**: Verifique a internet e a API key
