# **Game Design Document: Robot War (Adaptation of "La guerre des robots")**

---

## **1. Game Overview**

**Title:** Robot War
**Genre:** Programming Strategy / Turn-based Battle
**Players:** 1–4 (Human and/or AI)
**Platforms:** PC/Web (modular for Python, JavaScript, Godot, Unity, etc.)
**Core Loop:** Program robot(s) → Battle simulation → Last robot standing wins

---

## **2. Core Gameplay**

### **2.1. Flow**

1. **Game Setup:** Players configure game options (see section 3).
2. **Robot Programming:** Each player writes a sequence of instructions (program) for their robot, with memory limits.
3. **Arena Generation:** The game places obstacles and mines, and spawns robots in random positions on the grid.
4. **Battle Phase:** Robots execute their programs in turn-based, synchronous steps until only one remains or the round ends.
5. **Endgame/Scoring:** Last robot standing wins. If a turn limit is reached, the robot with the most energy wins.

---

## **3. Game Setup**

### **3.1. Player Options (Faithful to Original)**

* **Number of Players:** 1–4 (missing players filled by AI opponents)
* **Program Length:** Number of instruction steps per robot (default: 20, max: 40)
* **Robot Starting Energy:** Settable by players (suggested: 1,500–10,000)
* **Number of Obstacles:** Number of impassable blocks in the arena (suggested: 10–40)

*Note: Arena/grid size is fixed per original (e.g., 20x20 grid; see section 5.1). Can be made user-configurable as a modern enhancement.*

---

## **4. Robot Programming**

### **4.1. Programming Phase**

* Each player writes a **program**: a sequence of instructions (from a fixed set) to be stored in the robot’s memory.
* The number of instructions is limited by "Program Length" set during setup.
* **Program memory is circular:** Once the last instruction executes, the robot restarts from the first instruction.

### **4.2. Programming UI**

* **Per Player:** Display memory slots (number set by "Program Length").
* **Instructions:** Choose actions/tests per slot (from instruction set).
* **(Optional):** Support for copy/paste, saving, or loading predefined AI scripts.

---

### **4.3. Instruction Set (Actions/Tests)**

| Code | Action Name    | Description                                                           | Energy Cost | Damage |
| ---- | -------------- | --------------------------------------------------------------------- | ----------- | ------ |
| DM   | Directed Move  | Move in player-chosen direction (N/S/E/W)                             | 5           | —      |
| RM   | Random Move    | Move in a random direction                                            | 5           | —      |
| PS   | Pursue Enemy   | Move toward nearest enemy                                             | 10          | —      |
| MI   | Lay Mine       | Place a mine on current tile                                          | 200         | 200    |
| IN   | Invisibility   | Become invisible for 1 turn (cannot be targeted)                      | 200         | —      |
| AM   | Flee           | Move away from nearest enemy                                          | 15          | —      |
| TR   | Fire in Row    | Fire horizontally (first enemy in row hit)                            | 100         | 200    |
| TC   | Fire in Column | Fire vertically (first enemy in column hit)                           | 100         | 200    |
| PT   | Proximity Test | Test if mine or enemy is adjacent (used for conditional logic/branch) | 4           | —      |

* **Conditional Branching:**
  Use PT (proximity test) to allow program logic, e.g.,

  * “If PT is TRUE, then do X, else do Y”
    (Original game handles this via conditional programming slots.)

---

### **4.4. Special Mechanic: Circuit de Secours (Emergency Routine)**

* Optional: Each robot can be programmed with a single "emergency action" (e.g., to run when energy is low or program completes).
* Used when the main program ends or the robot takes critical damage.

---

## **5. Arena & Environment**

### **5.1. Arena**

* **Grid Size:** Fixed (e.g., 20x20; match the original Apple II implementation).
* **Tiles:**

  * Empty: Passable
  * Obstacle: Impassable
  * Mine: Hidden, triggers on step, causes damage
  * Robot: Each occupies one tile

### **5.2. Arena Generation**

* Obstacles and mines placed randomly, avoiding player starting positions.

---

## **6. Battle Phase**

### **6.1. Turn Structure**

* Each round/turn, **all robots execute their current program step simultaneously**:

  1. Fetch next instruction
  2. Execute (movement, attack, lay mine, etc.)
  3. Resolve interactions (collisions, attacks, mines, energy updates)
  4. Advance program counter (loops if at end)
* If a robot runs out of energy, it is removed from the game.

### **6.2. Interactions & Resolution**

* **Collisions:** Robots cannot occupy the same tile; resolution order is random or by energy.
* **Mines:** Stepping on a mine triggers damage; original robots may skip their own mines.
* **Attacks:** TR (row fire) and TC (column fire) hit the first enemy in their direction, causing damage.
* **Invisibility:** Robot is immune to attacks for the next turn.

---

## **7. Win Conditions**

* **Last robot remaining:** Wins.
* **If multiple robots after max turns:** Highest energy wins.
* **If tie:** Tiebreaker by most enemies destroyed, then random.

---

## **8. User Interface & Experience**

### **8.1. Setup Screen**

* Prompts for:

  1. Number of players
  2. Program steps
  3. Starting energy
  4. Obstacles

### **8.2. Programming Screen**

* For each player: grid of instruction slots, pick actions/tests.
* Show current energy cost/summary.

### **8.3. Arena/Battle Screen**

* 2D grid view of arena (robots, obstacles, optional mines if visible).
* Robot stats: position, energy, current instruction.
* Turn controls: Start, Pause, Step, Replay

### **8.4. Post-game/Results**

* Summary: who won, surviving robots, actions taken, replays

---

## **9. AI Opponents**

* Provide default “adversary” programs (from original, e.g., Horace Alpha, Berserk One).
* AI logic: Follows preset programs; can randomize among scripts for replayability.

---

## **10. Optional Modern Enhancements**

* Arena/grid size user-selectable (not in original).
* Save/load robot programs.
* Battle replays/step-through.
* Advanced AI (adaptable, not only preset).
* Visual effects and sounds.

---

## **11. Variables and Internal Data Structures**

* **Robot:**

  * Position (X, Y)
  * Energy (int)
  * Program (list of instructions)
  * Program Counter (int)
  * Emergency Action (optional)
  * Status (alive/invisible/etc.)

* **Arena:**

  * Grid (2D array): each cell = empty/obstacle/mine/robot
  * Obstacles: coordinates list
  * Mines: coordinates list (with owner if using mine immunity)

* **Game State:**

  * Player roster
  * Number of turns elapsed
  * Current phase (setup/program/battle/end)

---

## **12. Sample Robot Program (Pseudocode)**

```plaintext
1: PT                  # Test for proximity (mine/enemy)
2: IF PT=TRUE THEN TR  # If something is near, fire in row
3: ELSE RM             # Else, move randomly
4: MI                  # Lay mine
5: PS                  # Pursue nearest enemy
(repeat from step 1 after program ends)
```

---

## **13. References / Source Faithfulness**

* All configuration options and program limits reflect the original magazine’s described flow.
* Arena size is fixed as in the BASIC code; can be expanded for modern UI but is not original.
* Instruction set and energy/damage costs directly transcribed from the source.

---

### **Appendix: Default AI Programs (from Magazine)**

* **Horace Alpha:**

  1. PS (pursue), if no target then FT
  2. FT
  3. PT, if yes then MI, else PS
  4. RM
     (etc.)

* (Include more from the "Vos premiers adversaires..." table for built-in AIs.)

---

## **14. Implementation Notes**

* Modularize robot instruction parser.
* Arena stepper resolves all robots in parallel.
* Ensure circular program execution (after last instruction, start over).
* UI/UX should make programming accessible (drag-and-drop, buttons, or code).

---
