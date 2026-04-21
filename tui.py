'''
most of this file was made by ai!
but who cares! it works!!!
'''
import yaml
import sys
import os
from ai.Characters import Character
from helpers.audio import record, stop_recording

sys.dont_write_bytecode = True

# --- COLORS ---
C_HEAD = "\033[95m"  # Magenta
C_MENU = "\033[96m"  # Cyan
C_PROMPT = "\033[93m" # Yellow
C_USER = "\033[92m"   # Green
C_AI = "\033[94m"     # Blue
C_ERR = "\033[91m"    # Red
C_RST = "\033[0m"

def clear():
    os.system("clear" if os.name != "nt" else "cls")

def load_data():
    try:
        with open("personas.yaml", "r") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {}

def save_data(data):
    with open("personas.yaml", "w") as f:
        yaml.dump(data, f, default_flow_style=False)

def chat_loop(name, config):
    clear()
    print(f"\n{C_HEAD}--- Chatting with {name} ---{C_RST}")
    print(f"{C_MENU}(Press 'c' at prompt or say 'lobotomize' to clear history){C_RST}\n")
    
    system_prompt = config.get("system", "")
    voice_id = config.get("voice", "JBFqnCBsd6RMkjVDRZzb")
    
    ai = Character(system_prompt, voice_id=voice_id)

    while True:
        try:
            cmd = input(f"{C_PROMPT}Press Enter to record, 'c' to clear, 'q' to exit: {C_RST}").strip().lower()
            
            if cmd == 'q':
                break
            if cmd == 'c':
                del ai.history
                clear()
                print(f"\n{C_HEAD}--- Chatting with {name} ---{C_RST}")
                print(f"{C_ERR}Ai lobotomized{C_RST}\n")
                continue

            record()
            input(f"{C_ERR}🔴 Recording... Press Enter to stop.{C_RST}")
            
            stt_res = ai.stt(stop_recording())
            text = stt_res
            
            if not text.strip():
                print(f"{C_ERR}No speech detected. Try again.{C_RST}")
                continue
            
            if any(trigger in text.lower() for trigger in ["lobotomize", "clear history", "forget everything"]):
                del ai.history
                clear()
                print(f"\n{C_HEAD}--- Chatting with {name} ---{C_RST}")
                print(f"{C_ERR}Voice command detected: Ai lobotomized{C_RST}\n")
                continue

            print(f"{C_USER}You: {text}{C_RST}")
            
            reply = ai.generate(text)
            print(f"{C_AI}{name}: {reply}{C_RST}")
            
            # Buffer before audio to let things settle
            import time
            time.sleep(0.2)
            
            ai.play(ai.tts(reply))
            
            # Buffer after audio so it doesn't immediately prompt to record
            time.sleep(0.5)
            print("-" * 40)
            
        except KeyboardInterrupt:
            break

def select_persona(data, action_name):
    clear()
    personas = {k: v for k, v in data.items() if isinstance(v, dict)}
    if not personas:
        print(f"{C_ERR}No personas available.{C_RST}")
        input("\nPress Enter to return...")
        return None, None
        
    names = list(personas.keys())
    print(f"\n{C_HEAD}--- {action_name} ---{C_RST}")
    for i, name in enumerate(names, 1):
        print(f"{C_MENU}{i}.{C_RST} {name}")
    print(f"{C_MENU}q.{C_RST} Back")
    
    c = input(f"{C_PROMPT}Select an option: {C_RST}").strip().lower()
    if c == 'q': return None, None
    if c.isdigit() and 1 <= int(c) <= len(names):
        name = names[int(c)-1]
        return name, personas[name]
        
    print(f"{C_ERR}Invalid option.{C_RST}")
    input("\nPress Enter to return...")
    return None, None

def main():
    while True:
        clear()
        data = load_data()
        
        print(f"\n{C_HEAD}========== AGENTIC FUN =========={C_RST}")
        print(f"{C_MENU}1.{C_RST} Chat with Persona")
        print(f"{C_MENU}2.{C_RST} Create New Persona")
        print(f"{C_MENU}3.{C_RST} Edit Persona")
        print(f"{C_MENU}q.{C_RST} Quit")
        print(f"{C_HEAD}================================={C_RST}")
        
        choice = input(f"{C_PROMPT}Choose an option: {C_RST}").strip().lower()
        
        if choice == 'q':
            clear()
            print(f"{C_MENU}Goodbye!{C_RST}")
            break
            
        elif choice == '1':
            name, config = select_persona(data, "Select Persona")
            if name: chat_loop(name, config)
                
        elif choice == '2':
            clear()
            print(f"\n{C_HEAD}--- Create Persona ---{C_RST}")
            name = input(f"{C_PROMPT}Name: {C_RST}").strip()
            if not name: continue
            system = input(f"{C_PROMPT}System Prompt: {C_RST}").strip()
            voice = input(f"{C_PROMPT}Voice ID: {C_RST}").strip()
            
            data[name] = {"system": system}
            if voice: data[name]["voice"] = voice
            save_data(data)
            print(f"\n{C_USER}Persona '{name}' created successfully!{C_RST}")
            input("\nPress Enter to return...")
            
        elif choice == '3':
            name, config = select_persona(data, "Edit Persona")
            if not name: continue
            
            clear()
            print(f"\n{C_HEAD}--- Editing {name} ---{C_RST}")
            print(f"{C_MENU}1.{C_RST} Edit System Prompt")
            print(f"{C_MENU}2.{C_RST} Edit Voice ID")
            print(f"{C_MENU}3.{C_RST} Delete Persona")
            print(f"{C_MENU}q.{C_RST} Cancel")
            
            ec = input(f"{C_PROMPT}Choose an option: {C_RST}").strip().lower()
            if ec == '1':
                sys_prompt = input(f"{C_PROMPT}New System Prompt: {C_RST}").strip()
                data[name]['system'] = sys_prompt
                save_data(data)
                print(f"{C_USER}System prompt updated.{C_RST}")
            elif ec == '2':
                voice_id = input(f"{C_PROMPT}New Voice ID: {C_RST}").strip()
                data[name]['voice'] = voice_id
                save_data(data)
                print(f"{C_USER}Voice updated.{C_RST}")
            elif ec == '3':
                confirm = input(f"{C_ERR}Are you sure you want to delete {name}? (y/n): {C_RST}").strip().lower()
                if confirm == 'y':
                    del data[name]
                    save_data(data)
                    print(f"{C_USER}Persona deleted.{C_RST}")
            input("\nPress Enter to return...")
                    
        else:
            print(f"{C_ERR}Invalid option. Please try again.{C_RST}")
            input("\nPress Enter to return...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
