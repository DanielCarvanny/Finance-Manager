import customtkinter as ctk
import json
import os

def gerar_tema():
    # 1. Carrega o tema verde padrão (que tem todas as 5.000 configurações secretas e fontes)
    ctk.set_default_color_theme("green")
    
    # 2. Clona o dicionário gigantesco de temas que está rodando na memória do CustomTkinter
    tema_completo = ctk.ThemeManager.theme
    
    # 3. Sobrepõe apenas as NOSSAS cores exclusivas do "Dark Mode Trader"
    tema_completo["CTk"]["fg_color"] = ["#0B0E11", "#0B0E11"]
    tema_completo["CTkToplevel"]["fg_color"] = ["#0B0E11", "#0B0E11"]
    
    tema_completo["CTkFrame"]["fg_color"] = ["#1E2329", "#1E2329"]
    tema_completo["CTkFrame"]["top_fg_color"] = ["#1E2329", "#1E2329"]
    
    tema_completo["CTkButton"]["fg_color"] = ["#635BFF", "#635BFF"]
    tema_completo["CTkButton"]["hover_color"] = ["#7A73FF", "#7A73FF"]
    tema_completo["CTkButton"]["text_color"] = ["#FFFFFF", "#FFFFFF"]
    
    tema_completo["CTkScrollableFrame"]["label_fg_color"] = ["#1E2329", "#1E2329"]
    
    tema_completo["CTkComboBox"]["fg_color"] = ["#1E2329", "#1E2329"]
    tema_completo["CTkComboBox"]["button_color"] = ["#635BFF", "#635BFF"]
    tema_completo["CTkComboBox"]["button_hover_color"] = ["#7A73FF", "#7A73FF"]
    
    tema_completo["CTkProgressBar"]["fg_color"] = ["#1E2329", "#1E2329"]
    tema_completo["CTkProgressBar"]["progress_color"] = ["#635BFF", "#635BFF"]

    # 4. Salva o arquivo json perfeito de volta na nossa pasta UI!
    pasta_ui = os.path.join(os.path.dirname(__file__), "src", "ui")
    caminho_arquivo = os.path.join(pasta_ui, "theme.json")
    
    with open(caminho_arquivo, 'w', encoding='utf-8') as f:
        json.dump(tema_completo, f, indent=2)
        
    print(f"✅ Sucesso! O Tema InterFIN foi gerado com segurança em: {caminho_arquivo}")

if __name__ == "__main__":
    gerar_tema()