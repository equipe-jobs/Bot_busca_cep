$exclude = @("venv", "BotTeste.zip")
$files = Get-ChildItem -Path . -Exclude $exclude
Compress-Archive -Path $files -DestinationPath "BotTeste.zip" -Force