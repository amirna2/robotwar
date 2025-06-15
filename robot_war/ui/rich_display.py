"""Enhanced Rich-based display system for Robot War."""

from typing import Dict, List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich.progress import Progress, BarColumn, TextColumn
from rich.text import Text
from rich.align import Align
from rich.layout import Layout
from rich.live import Live

from ..core.game_state import GameState, GamePhase
from ..core.robot import Robot, RobotStatus


class RichArenaDisplay:
    """Enhanced display system using Rich library for better terminal experience."""
    
    # Enhanced Unicode symbols for better visual representation
    SYMBOLS = {
        'empty': '⚫',           # Empty cell
        'obstacle': '🧱',        # Obstacle
        'mine': '💣',           # Mine
        'dead_robot': '💀',      # Dead robot (skull)
        'robot_alive': '🤖',     # Alive robot
        'robot_invisible': '👻', # Invisible robot
        'robot_frozen': '🧊',    # Frozen robot
    }
    
    # Robot colors for better distinction
    ROBOT_COLORS = [
        "bright_cyan", "bright_yellow", "bright_magenta", "bright_green",
        "bright_red", "bright_blue", "bright_white", "orange3"
    ]
    
    def __init__(self):
        self.console = Console()
        self.live = None
    
    def get_robot_symbol_and_style(self, robot: Robot) -> tuple[str, str]:
        """Get symbol and Rich style for a robot based on its status."""
        if robot.status == RobotStatus.DEAD:
            return self.SYMBOLS['dead_robot'], "dim white"
        elif robot.status == RobotStatus.INVISIBLE:
            return self.SYMBOLS['robot_invisible'], "dim blue"
        elif robot.status == RobotStatus.FROZEN:
            return self.SYMBOLS['robot_frozen'], "bright_blue"
        else:
            color = self.ROBOT_COLORS[robot.player_id % len(self.ROBOT_COLORS)]
            return self.SYMBOLS['robot_alive'], f"bold {color}"
    
    def render_arena_grid(self, game_state: GameState) -> Text:
        """Recreate the EXACT original terminal grid with 3x3 cells and box drawing."""
        grid_text = Text()
        arena = game_state.arena
        
        # Top border (exactly like original)
        grid_text.append("┌", style="dim white")
        for x in range(arena.width):
            grid_text.append("───", style="dim white")
            if x < arena.width - 1:
                grid_text.append("┬", style="dim white")
        grid_text.append("┐\n", style="dim white")
        
        # Render each row with grid lines (exactly like original)
        for y in range(arena.height):
            # Cell content row
            grid_text.append("│", style="dim white")
            for x in range(arena.width):
                # Get cell content exactly like original (3 chars: " X ")
                cell_content = self._get_cell_content(arena, x, y, game_state.robots)
                grid_text.append(cell_content)
                grid_text.append("│", style="dim white")
            grid_text.append("\n")
            
            # Horizontal separator (except for last row)
            if y < arena.height - 1:
                grid_text.append("├", style="dim white")
                for x in range(arena.width):
                    grid_text.append("───", style="dim white")
                    if x < arena.width - 1:
                        grid_text.append("┼", style="dim white")
                grid_text.append("┤\n", style="dim white")
        
        # Bottom border (exactly like original)
        grid_text.append("└", style="dim white")
        for x in range(arena.width):
            grid_text.append("───", style="dim white")
            if x < arena.width - 1:
                grid_text.append("┴", style="dim white")
        grid_text.append("┘", style="dim white")
        
        return grid_text
    
    def _get_cell_content(self, arena, x: int, y: int, robots) -> Text:
        """Get the content for a grid cell (exactly 3 characters: ' X ')."""
        # Check for robots first (highest priority)
        for robot in robots:
            if robot.get_position() == (x, y) and robot.is_alive():
                if robot.status == RobotStatus.INVISIBLE:
                    return Text(" ? ", style="dim cyan")
                elif robot.status == RobotStatus.FROZEN:
                    color = self.ROBOT_COLORS[robot.player_id % len(self.ROBOT_COLORS)]
                    return Text(f" {robot.player_id} ", style=f"bright_blue")
                else:
                    color = self.ROBOT_COLORS[robot.player_id % len(self.ROBOT_COLORS)]
                    return Text(f" {robot.player_id} ", style=f"bold {color}")

        # Check for mines
        if arena.has_mine(x, y):
            return Text(" ◉ ", style="bright_red")

        # Check for obstacles  
        if not arena.is_passable(x, y):
            if arena.grid[y][x] == 'D':  # Dead robot
                return Text(" X ", style="dim white")
            else:  # Regular obstacle
                return Text(" ⎕ ", style="yellow")

        # Empty cell
        return Text(" · ", style="dim white")
    
    def create_robot_status_panel(self, robots: List[Robot]) -> Panel:
        """Create a panel showing robot status with energy bars."""
        if not robots:
            return Panel("No robots", title="Robot Status")
        
        # Create status for each robot
        robot_status = []
        
        for robot in robots:
            if not robot.is_alive():
                continue  # Skip dead robots
            
            # Robot identification
            color = self.ROBOT_COLORS[robot.player_id % len(self.ROBOT_COLORS)]
            robot_symbol, _ = self.get_robot_symbol_and_style(robot)
            
            # Energy percentage
            energy_pct = (robot.energy / robot.max_energy) * 100
            
            # Energy bar color based on level
            if energy_pct > 70:
                bar_color = "green"
            elif energy_pct > 30:
                bar_color = "yellow"
            else:
                bar_color = "red"
            
            # Create energy bar representation
            bar_length = 20
            filled = int((energy_pct / 100) * bar_length)
            bar = "█" * filled + "▌" * (bar_length - filled)
            
            # Status indicators
            status_text = ""
            if robot.status == RobotStatus.INVISIBLE:
                status_text = " 👻"
            elif robot.status == RobotStatus.FROZEN:
                status_text = " 🧊"
            
            # Combine robot info
            robot_info = Text()
            robot_info.append(f"{robot_symbol} {robot.name}", style=f"bold {color}")
            robot_info.append(f" {bar} {energy_pct:.0f}% ({robot.energy}/{robot.max_energy})", style=bar_color)
            robot_info.append(status_text)
            
            robot_status.append(robot_info)
        
        # Combine all robot status
        if robot_status:
            status_content = Text("\n").join(robot_status)
        else:
            status_content = Text("All robots destroyed", style="dim red")
        
        return Panel(status_content, title="🤖 Robot Status", border_style="blue")
    
    def create_game_info_panel(self, game_state: GameState) -> Panel:
        """Create a panel with game information."""
        info_text = Text()
        
        # Game phase with appropriate emoji
        phase_emoji = {
            GamePhase.SETUP: "⚙️",
            GamePhase.PROGRAMMING: "💻", 
            GamePhase.BATTLE: "⚔️",
            GamePhase.FINISHED: "🏆"
        }
        
        emoji = phase_emoji.get(game_state.phase, "❓")
        info_text.append(f"{emoji} Phase: {game_state.phase.value.title()}\n", style="bold cyan")
        
        if game_state.phase == GamePhase.BATTLE:
            info_text.append(f"🕒 Turn: {game_state.current_turn + 1}/{game_state.max_turns}\n", style="yellow")
            
            # Living robots count
            living_count = len(game_state.get_living_robots())
            info_text.append(f"🤖 Robots Alive: {living_count}/{len(game_state.robots)}\n", style="green")
        
        if game_state.phase == GamePhase.FINISHED:
            if game_state.winner_id:
                info_text.append(f"🏆 Winner: Robot {game_state.winner_id}!", style="bold gold1")
            else:
                info_text.append("💀 No Survivors!", style="bold red")
        
        return Panel(info_text, title="🎮 Game Info", border_style="green")
    
    def create_combat_log_panel(self, combat_log: List[str]) -> Panel:
        """Create a panel for combat log with the latest actions."""
        if not combat_log:
            content = Text("No combat actions this turn", style="dim")
        else:
            # Show last 5 combat actions
            recent_actions = combat_log[-5:]
            content = Text()
            
            for action in recent_actions:
                # Style different types of actions
                if "fires" in action:
                    content.append(f"⚔️ {action}\n", style="bright_red")
                elif "hits" in action:
                    content.append(f"   {action}\n", style="red")
                elif "destroyed" in action:
                    content.append(f"   {action}\n", style="bold red")
                else:
                    content.append(f"• {action}\n", style="white")
        
        return Panel(content, title="⚔️ Combat Log", border_style="red")
    
    def create_game_layout(self, game_state: GameState) -> Layout:
        """Create the complete game layout without clearing screen."""
        
        # Create main layout
        layout = Layout()
        
        # Split into main sections
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=8)
        )
        
        # Header - Game title
        title = Text("🤖 ROBOT WAR 🤖", style="bold bright_cyan")
        layout["header"].update(Panel(Align.center(title), style="bright_cyan"))
        
        # Main section - split between arena and info
        layout["main"].split_row(
            Layout(name="arena", ratio=2),
            Layout(name="info", ratio=1)
        )
        
        # Arena display
        arena_grid = self.render_arena_grid(game_state)
        arena_panel = Panel(
            Align.center(arena_grid), 
            title=f"🏟️ Arena ({game_state.arena.width}×{game_state.arena.height})",
            border_style="bright_white"
        )
        layout["arena"].update(arena_panel)
        
        # Info section - split into multiple panels
        layout["info"].split_column(
            Layout(name="game_info", size=6),
            Layout(name="robot_status", ratio=1)
        )
        
        layout["game_info"].update(self.create_game_info_panel(game_state))
        layout["robot_status"].update(self.create_robot_status_panel(game_state.robots))
        
        # Footer - Combat log
        layout["footer"].update(self.create_combat_log_panel(game_state.combat_log))
        
        return layout
    
    def start_live_display(self):
        """Start the live display context."""
        if self.live is None:
            self.live = Live(console=self.console, refresh_per_second=2)
            self.live.start()
    
    def update_live_display(self, game_state: GameState):
        """Update the live display with new game state."""
        if self.live:
            layout = self.create_game_layout(game_state)
            self.live.update(layout)
    
    def stop_live_display(self):
        """Stop the live display context."""
        if self.live:
            self.live.stop()
            self.live = None
    
    def display_battle_summary(self, game_state: GameState):
        """Display final battle summary with Rich formatting."""
        self.console.clear()
        
        # Create summary panel
        summary = Text()
        summary.append("🏆 BATTLE COMPLETE! 🏆\n\n", style="bold bright_yellow")
        
        if game_state.winner_id:
            # Find winner robot by player_id to get name
            winner_robot = next((r for r in game_state.robots if r.player_id == game_state.winner_id), None)
            winner_name = winner_robot.name if winner_robot else f"Robot {game_state.winner_id}"
            winner_color = self.ROBOT_COLORS[game_state.winner_id % len(self.ROBOT_COLORS)]
            summary.append(f"🎉 {winner_name} WINS! 🎉\n", style=f"bold {winner_color}")
        else:
            summary.append("💀 All robots destroyed - No winner! 💀\n", style="bold red")
        
        summary.append(f"\nBattle lasted {game_state.current_turn} turns\n", style="cyan")
        
        # Final robot status
        summary.append("\n📊 Final Status:\n", style="bold blue")
        for robot in game_state.robots:
            color = self.ROBOT_COLORS[robot.player_id % len(self.ROBOT_COLORS)]
            status = "ALIVE" if robot.is_alive() else "DESTROYED"
            status_style = "green" if robot.is_alive() else "red"
            summary.append(f"  🤖 {robot.name}: {status} (Energy: {robot.energy})\n", 
                         style=f"{color}")
        
        panel = Panel(
            Align.center(summary),
            title="🎮 Battle Results",
            border_style="bright_yellow",
            padding=(1, 2)
        )
        
        self.console.print(panel)
    
    def wait_for_input(self, prompt: str = "Press Enter to continue...") -> str:
        """Wait for user input with Rich styling."""
        styled_prompt = Text(prompt, style="bold bright_cyan")
        self.console.print(styled_prompt, end="")
        return input()