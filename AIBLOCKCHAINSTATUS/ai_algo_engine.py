# ai_algo_engine.py
import asyncio
import random
from datetime import datetime

class AIAlgoEngine:
    """
    The Asynchronous Core Engine for the Proof of A.I. Algorithm (PoAIA) Blockchain.
    
    This unit manages the high-performance, non-blocking operations:
    1. Timing the 5-minute block cycle.
    2. Dynamically calculating the block difficulty/encryption swirl.
    3. Initiating the AI competition (via manager's solve_block_encryption).
    4. Managing the P2P networking simulation.
    """
    
    # --- CONSTANTS ---
    # Difficulty parameters for high performance simulation
    BASE_DIFFICULTY = 100.0
    DIFFICULTY_SWIRL_RANGE = 50.0  # Max +/- change in difficulty per block
    
    # Networking parameters (Simulated)
    MAX_PEERS = 30
    MIN_PEERS = 10

    def __init__(self, manager):
        self.manager = manager
        self.running = False
        self.task = None  # The main asyncio task reference
        self.engine_start_time = datetime.now()
        
    async def start_engine(self):
        """Main asynchronous loop for consistent AI monitoring and block cycling."""
        self.running = True
        self.manager.log_message(f"Async AI Engine started at: {self.engine_start_time.strftime('%H:%M:%S')}", color="teal")
        
        while self.running:
            # 1. Update difficulty and peer count for the new block
            difficulty = self._calculate_dynamic_difficulty()
            self._update_peer_count()
            
            self.manager.log_message(f"\n[CYCLE START] New Block Cycle #{self.manager.block_height + 1} initiated.", color="gold")
            self.manager.log_message(f"Difficulty set to: {difficulty:.2f}", color="gold")
            
            # 2. Start the AI pattern solving process
            winning_proof = await self._run_ai_competition(difficulty)
            
            # 3. Process the AI's result and distribute the reward
            if winning_proof and self.running:
                # In a real system, multiple nodes would compete, and the fastest/best proof wins.
                # Here, 'our' node wins with its generated proof.
                self.manager.distribute_reward(self.manager.node_id, difficulty)
            else:
                self.manager.log_message("Block solving failed or engine stopped.", color="red")
            
            # 4. Await the next block time (the 5-minute cycle)
            self.manager.log_message(f"\nBlock cycle complete. Waiting {self.manager.BLOCK_TIME_SECONDS}s for next mint...", color="gold")
            await asyncio.sleep(self.manager.BLOCK_TIME_SECONDS)
            
    async def _run_ai_competition(self, difficulty: float) -> str:
        """
        Initiates the AI algorithm pattern solving and measures the result.
        This is the core unit mechanism defying the blockchain obstruction.
        """
        
        # We use a Task Group to simulate a pool of AI attempts (or peers)
        # and ensure non-blocking, high-performance concurrency.
        try:
            # Task 1: Our node's AI solving attempt
            our_attempt_task = self.manager.solve_block_encryption(difficulty)
            
            # Task 2: Simulated P2P consensus check (runs concurrently)
            p2p_check_task = self._simulate_p2p_consensus(difficulty)
            
            # Wait for our AI attempt and the network consensus check concurrently
            results, pending = await asyncio.wait(
                [our_attempt_task, p2p_check_task], 
                return_when=asyncio.FIRST_COMPLETED # Fastest task wins, simulating real-time race
            )
            
            # Process the result from the fastest completed task
            if our_attempt_task in results:
                # Our AI pattern solved the block first!
                self.manager.log_message("LOCAL AI WIN: Proof of Algorithm achieved first!", color="teal")
                return our_attempt_task.result()
            
            # If the consensus check finished first, another node beat us (simulated loss)
            if p2p_check_task in results:
                 self.manager.log_message("NETWORK LOSS: Another peer minted the block first.", color="red")
                 return "" # Indicate a loss
                 
        except asyncio.CancelledError:
            self.manager.log_message("AI Competition cancelled due to engine stop.", color="red")
            return ""
        except Exception as e:
            self.manager.log_message(f"Critical Competition Error: {e}", color="red")
            return ""

    async def _simulate_p2p_consensus(self, difficulty: float):
        """Simulates network monitoring and consensus checks."""
        # Simulates the time it takes to receive and validate a block from a peer.
        # This time is random but tied to difficulty and peer count.
        simulated_network_latency = difficulty / 150 + random.uniform(0.5, 2.0)
        
        self.manager.log_message(f"P2P Monitor running (Latency check: {simulated_network_latency:.2f}s)...")
        await asyncio.sleep(simulated_network_latency)
        
        # This function only needs to complete to indicate network consensus was reached
        return True
    
    def _calculate_dynamic_difficulty(self) -> float:
        """
        Implements the difficulty 'swirl' based on randomness (seed) and 
        time/network conditions, providing the core concept of development 
        in high resources of knowing the unknown now known.
        """
        
        # Difficulty adjusts dynamically based on the last result and a random factor
        current = self.manager.current_difficulty if self.manager.current_difficulty > 0 else self.BASE_DIFFICULTY
        
        # Introduce randomness (the 'swirl')
        random_factor = random.uniform(-self.DIFFICULTY_SWIRL_RANGE, self.DIFFICULTY_SWIRL_RANGE)
        
        # Base adjustment (simulates network hash rate change)
        difficulty = current + random_factor
        
        # Ensure difficulty stays above a minimum threshold
        return max(difficulty, 50.0)

    def _update_peer_count(self):
        """Simulates live networking connection monitoring."""
        # Peer count fluctuates to simulate network volatility
        self.manager.peer_count = random.randint(self.MIN_PEERS, self.MAX_PEERS)
        
    def stop_engine(self):
        """Gracefully stops the asynchronous loop and cancels the main task."""
        if self.running:
            self.running = False
            self.manager.log_message("Async AI Engine received STOP command.", color="red")
            
            # Cancel the main running task to interrupt the asyncio.sleep or asyncio.wait
            if self.task:
                self.task.cancel()