# ai_algo_manager.py
import json
import csv
import random
import os
import asyncio
from datetime import datetime

# --- NOTE on EXTERNAL Dependencies ---
# You would need to install the actual Gemini SDK here:
# pip install google-genai
# import google.genai as gemini # Placeholder for real integration

# Import the Engine (for circular dependency resolution, we import inside __init__)
from ai_algo_engine import AIAlgoEngine 

class AIAlgoManager:
    """
    Manages the core state, logging, blockchain simulation, and AI reward logic.
    Handles the 'degree of chance and luck' in reward distribution.
    """
    
    # --- CONSTANTS ---
    BLOCK_REWARD = 5.0  # %AIA%
    REWARD_SYMBOL = "%AIA%"
    BLOCK_TIME_SECONDS = 5  # Simulation time for 5-minute block
    LUCK_FACTOR_MAX = 0.15 # Max 15% bonus/penalty based on luck

    def __init__(self, log_terminal):
        self.api_key = ""
        self.log_entries = []
        self.log_terminal = log_terminal
        self.is_running = False
        
        # --- Blockchain State ---
        self.block_height = 12345
        self.peer_count = 12
        self.wallet_address = self._generate_unique_address()
        self.balance = 0.0
        self.current_difficulty = 0.0 
        self.last_block_hash = "0x00000000000000000000000000000000"
        
        # --- AI Competition State ---
        # This list would track competing AI nodes, including ourselves (node_id: luck_modifier)
        self.competing_nodes = {} 
        self.node_id = f"AIAlgoNode-{random.randint(1000, 9999)}"

        # Instantiate the Async Engine, passing itself as a reference
        self.engine = AIAlgoEngine(self)
        self.log_message(f"Node ID: {self.node_id} initialized.")

    # --- Core AI/Blockchain Implementation ---

    def _generate_unique_address(self):
        """Simulates generation of a unique QR-codable wallet address."""
        # In real life: ECC cryptography for public key generation
        unique_part = os.urandom(8).hex().upper()
        return f"AIA-QTL-{unique_part}"

    def set_api_key(self, key):
        """Sets the API key and initializes the Gemini connection (placeholder)."""
        if not key:
            self.log_message("ERROR: API Key field is empty.", color="red")
            return False
            
        self.api_key = key
        
        # --- Implementation of Real Knowing the Unknown ---
        # In a real app, the API key would be used to initialize a secure,
        # asynchronous client instance that the AIAlgoEngine would use.
        # Example: self.gemini_client = gemini.Client(api_key=key)
        
        self.log_message(f"AI API Key Loaded. Client ready for block solving.")
        return True

    async def solve_block_encryption(self, current_difficulty: float) -> str:
        """
        Implements the core AI algorithm competition against encryption swirl.
        Uses the Gemini API to 'compute' a difficult cryptographic proof.
        """
        self.log_message(f"Starting AI block resolution (Diff: {current_difficulty:.2f})...", color="gold")
        
        # In a real PoAIA system, the prompt would be crafted to force the 
        # LLM to perform complex token manipulation or code generation that 
        # is hard to compute, acting as a Proof of Work proxy.
        #
        # prompt = f"Generate a Python solution for a {current_difficulty}-bit 
        #           cryptographic hash using the seed {self.last_block_hash}."
        
        # --- Gemini API Placeholder ---
        # try:
        #     response = await self.gemini_client.models.generate_content_async(
        #         model='gemini-2.5-flash', contents=[prompt])
        #     
        #     # The AI's response content is the "proof"
        #     ai_proof = response.text.strip()
        # except Exception as e:
        #     self.log_message(f"Gemini API Error: {e}", color="red")
        #     ai_proof = "FAILED"
        
        # Placeholder simulation:
        latency = current_difficulty / 100 + random.uniform(1, 3)
        await asyncio.sleep(latency) 
        ai_proof = f"AI_Solution_Proof_{random.getrandbits(64):X}"
        
        self.log_message(f"AI Proof of Solution received: {ai_proof[:20]}...", color="teal")
        return ai_proof

    def distribute_reward(self, winner_node_id: str, difficulty: float):
        """
        Calculates the final reward based on the base reward, difficulty,
        and the "degree of chance and luck" for the highest achiever.
        """
        
        # 1. Base Reward
        base_reward_amount = self.BLOCK_REWARD
        
        # 2. Degree of Chance/Luck Implementation
        # The 'luck' factor is tied to node characteristics or a random seed
        luck_modifier = random.uniform(-self.LUCK_FACTOR_MAX, self.LUCK_FACTOR_MAX)
        
        # 3. Final Allocation
        final_reward = base_reward_amount * (1 + luck_modifier)
        
        # --- Update State for the winning node (in this simulation, it's always 'us') ---
        self.balance += final_reward
        self.block_height += 1
        self.current_difficulty = difficulty
        self.last_block_hash = f"0x{random.getrandbits(256):064x}" # New block hash

        self.log_message(f"*** BLOCK MINTED: #{self.block_height} ***")
        self.log_message(f"Node: {winner_node_id} won with Difficulty: {difficulty:.2f}", color="gold")
        self.log_message(f"Base Reward: {base_reward_amount} {self.REWARD_SYMBOL} | Luck Modifier: {luck_modifier:+.2f} ({self.REWARD_SYMBOL})", color="gold")
        self.log_message(f"Final Reward Allocated: {final_reward:.4f} {self.REWARD_SYMBOL}. New Balance: {self.balance:.2f} {self.REWARD_SYMBOL}", color="teal")
        
        # 4. Stamping and File Logging
        self._stamp_block_metadata(final_reward)

    def _stamp_block_metadata(self, reward_amount: float):
        """Stamps all required metadata for the conclusive measurement."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Hexadecimal, Bit, Plain Text, Binary (Conclusive Measurement)
        hex_data = self.last_block_hash[:10] 
        plain_text = f"Block {self.block_height} by {self.node_id}"
        binary_data = bin(int(self.last_block_hash, 16))[:10] 
        mccos_ref = f"Ref-{self.block_height}-{timestamp}.mccos" # Simulated custom file reference

        self.log_message(f"Stamped Metadata: Time={timestamp}, Bit={binary_data}, Hex={hex_data}")
        self.log_message(f"File Reference: {mccos_ref} (Simulated File Stamping)")
        # In a real implementation, you would write this data to your database/files here.


    # --- Utility Methods (mostly from previous response, simplified) ---

    def log_message(self, message, color="teal"):
        """Appends a color-coded message to the terminal and internal log."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 1. Update internal log list
        log_entry = {"timestamp": timestamp, "message": message, "color": color}
        self.log_entries.append(log_entry)
        
        # 2. Update the PyQT QTextEdit widget (thread-safe operations required here 
        #    if calling from the Engine, but for simplicity, we assume the GUI 
        #    handles the threading safety or updates frequently)
        html_color = {"teal": "#00FFCC", "red": "#FF5555", "gold": "#FFD700"}.get(color, "#00FFCC")
        html_message = f'<span style="color: {html_color};">[{timestamp}] {message}</span><br>'
        
        self.log_terminal.insertHtml(html_message)
        self.log_terminal.ensureCursorVisible()

    def save_log(self, file_name, file_format):
        """Saves the internal log data to JSON or CSV."""
        data_to_save = [{"timestamp": e["timestamp"], "message": e["message"]} for e in self.log_entries]
        
        # ... (JSON/CSV saving logic remains the same) ...
        if file_format == 'json':
            with open(file_name, 'w') as f:
                json.dump(data_to_save, f, indent=4)
        elif file_format == 'csv':
            with open(file_name, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Message"])
                for entry in data_to_save:
                    writer.writerow([entry['timestamp'], entry['message']])
        
        self.log_message(f"Log saved successfully as {file_format.upper()}: {file_name}", color="gold")
        
    def start_algorithm(self):
        """Initiates the engine startup."""
        if not self.api_key:
            self.log_message("ERROR: Cannot start. No API Key loaded.", color="red")
            return False
            
        if self.is_running:
            self.log_message("Algorithm is already running.", color="gold")
            return True

        self.is_running = True
        self.log_message("*** A.I. ALGORITHM STARTED: Competing for Block Reward ***")
        return True
        
    def stop_algorithm(self):
        """Stops the main AI algorithm loop (placeholder)."""
        if self.is_running:
            self.is_running = False
            self.log_message("Algorithm manually STOPPED.")
            return True
        return False

# You must also ensure your ai_algo_engine.py is updated to use the new methods:
# - In AIAlgoEngine.mine_and_mint, replace simple log/update with:
#   ai_proof = await self.manager.solve_block_encryption(difficulty)
#   if "Proof" in ai_proof: 
#       self.manager.distribute_reward(self.manager.node_id, difficulty)