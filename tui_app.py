#!/usr/bin/env python3
"""
TUI Application for Synthetic E-Commerce Data Generator
Uses Textual library for interactive terminal interface
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Header, Footer, Button, Static, Label, 
    RadioButton, RadioSet, Input, SelectionList,
    DataTable, ProgressBar
)
from textual.screen import Screen
from textual.binding import Binding
from textual import on
from textual.message import Message
import asyncio
from datetime import datetime
from pathlib import Path
import sys

# Import from generate.py
try:
    from generate import create_scenario_configs, SyntheticDataGenerator, ScenarioConfig
except ImportError:
    print("Error: generate.py not found. Make sure it's in the same directory.")
    sys.exit(1)

# Category mapping function for string to numeric conversion
def category_mapping(category: str) -> int:
    """Map category names to numeric values

    Args:
        category: Category name as string

    Returns:
        Numeric category ID (1-5), defaults to 1 (electronics) for unknown categories
    """
    category_map = {
        "electronics": 1,
        "clothing": 2,
        "home": 3,
        "beauty": 4,
        "books": 5
    }
    return category_map.get(category.lower(), 1)


class LoadingScreen(Screen):
    """Initial loading screen"""
    
    CSS = """
    LoadingScreen {
        align: center middle;
    }
    
    #loading-container {
        width: 60;
        height: 15;
        border: heavy $primary;
        background: $surface;
        padding: 2;
    }
    
    #title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }
    
    #subtitle {
        text-align: center;
        color: $text-muted;
        margin-bottom: 2;
    }
    
    #version {
        text-align: center;
        color: $text-muted;
        margin-top: 2;
    }
    """
    
    def compose(self) -> ComposeResult:
        with Container(id="loading-container"):
            yield Static("🚀 SYNTHETIC E-COMMERCE DATA GENERATOR", id="title")
            yield Static("powered by Textual", id="subtitle")
            yield ProgressBar(total=100, show_eta=False)
            yield Static("v1.0.0 (CLI + TUI)", id="version")
    
    async def on_mount(self) -> None:
        """Simulate loading and switch to main menu"""
        progress = self.query_one(ProgressBar)
        for i in range(101):
            progress.update(progress=i)
            await asyncio.sleep(0.02)
        
        await asyncio.sleep(0.5)
        self.app.switch_screen("scenario_selection")


class ScenarioSelectionScreen(Screen):
    """Main scenario selection screen"""
    
    BINDINGS = [
        Binding("f1", "help", "Help", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]
    
    CSS = """
    ScenarioSelectionScreen {
        layout: grid;
        grid-size: 2;
        grid-columns: 1fr 1fr;
    }
    
    #scenarios-container {
        height: 100%;
        border: heavy $primary;
        background: $surface;
    }
    
    #details-container {
        height: 100%;
        border: heavy $primary;
        background: $surface;
        padding: 1;
    }
    
    .scenario-title {
        text-style: bold;
        color: $accent;
        padding: 1;
        background: $boost;
    }
    
    .scenario-button {
        width: 100%;
        margin: 0 1;
    }
    
    .detail-label {
        color: $text-muted;
        margin-bottom: 1;
    }
    
    .detail-value {
        color: $text;
        text-style: bold;
        margin-bottom: 1;
    }
    """
    
    def __init__(self):
        super().__init__()
        self.scenarios = create_scenario_configs()
        self.selected_scenario = None
        self.scenario_descriptions = {
            "flash_sale": "High-intensity 4h flash sale with 8.5x traffic spike",
            "returns_wave": "Post-holiday 14d returns surge with 3x return rate",
            "supply_disruption": "14d supplier delays affecting 35 SKUs",
            "payment_outage": "6h payment gateway outage with increased abandonment",
            "viral_moment": "24h viral SKU traffic spike from TikTok",
            "customer_segments": "180-day cohort analysis with Gen Z growth",
            "seasonal_planning": "60-day seasonal campaign (back-to-school)",
            "multi_channel": "90-day cross-channel migration analysis",
            "baseline": "30-day normal operations baseline",
            "custom": "Build your own custom scenario"
        }
    
    def compose(self) -> ComposeResult:
        with Vertical(id="scenarios-container"):
            yield Static("📊 Scenarios", classes="scenario-title")
            for scenario_name in self.scenarios.keys():
                yield Button(scenario_name.replace("_", " ").title(), 
                           id=f"btn-{scenario_name}",
                           classes="scenario-button")
            yield Button("Custom Scenario", id="btn-custom", classes="scenario-button")
        
        with ScrollableContainer(id="details-container"):
            yield Static("📋 Details", classes="scenario-title")
            yield Static("Select a scenario to view details", id="scenario-details")
    
    def action_help(self) -> None:
        """Show help information"""
        self.app.push_screen("help")
    
    def action_quit(self) -> None:
        """Quit the application"""
        self.app.exit()
    
    @on(Button.Pressed)
    def handle_scenario_selection(self, event: Button.Pressed) -> None:
        """Handle scenario button press"""
        if event.button.id is None:
            return

        scenario_name = event.button.id.replace("btn-", "")

        if scenario_name == "custom":
            self.app.push_screen(CustomScenarioScreen())
        else:
            self.selected_scenario = scenario_name
            self.update_details(scenario_name)
            # Move to dataset size selection
            self.app.push_screen(DatasetSizeScreen(scenario_name, self.scenarios[scenario_name]))
    
    def update_details(self, scenario_name: str) -> None:
        """Update the details panel"""
        details_widget = self.query_one("#scenario-details", Static)
        
        if scenario_name in self.scenarios:
            scenario = self.scenarios[scenario_name]
            description = self.scenario_descriptions.get(scenario_name, "No description available")
            
            details_text = f"""
[bold cyan]{scenario_name.replace('_', ' ').title()}[/bold cyan]

{description}

[dim]Duration:[/dim] [bold]{scenario.duration}[/bold]
[dim]Intensity:[/dim] [bold]{scenario.intensity_multiplier}x[/bold]

[dim]Special Parameters:[/dim]
"""
            if scenario.special_params:
                for key, value in scenario.special_params.items():
                    details_text += f"  • {key}: {value}\n"
            else:
                details_text += "  • None\n"
            
            details_widget.update(details_text)


class DatasetSizeScreen(Screen):
    """Dataset size selection screen"""
    
    BINDINGS = [
        Binding("escape", "cancel", "Back", show=True),
    ]
    
    CSS = """
    DatasetSizeScreen {
        align: center middle;
    }
    
    #size-container {
        width: 70;
        height: auto;
        border: heavy $primary;
        background: $surface;
        padding: 2;
    }
    
    .title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 2;
    }
    
    .section-title {
        text-style: bold;
        color: $text;
        margin-top: 1;
        margin-bottom: 1;
    }
    
    .preset-info {
        background: $boost;
        padding: 1;
        margin: 1 0;
        border: solid $primary;
    }
    
    .button-container {
        layout: horizontal;
        align: center middle;
        margin-top: 2;
    }
    
    Button {
        margin: 0 1;
    }
    """
    
    def __init__(self, scenario_name: str, scenario_config: ScenarioConfig):
        super().__init__()
        self.scenario_name = scenario_name
        self.scenario_config = scenario_config
        self.preset_configs = {
            "small": {"customers": 1000, "orders_per_hour": 100, "duration_mult": 0.25},
            "medium": {"customers": 10000, "orders_per_hour": 500, "duration_mult": 0.5},
            "large": {"customers": 50000, "orders_per_hour": 1500, "duration_mult": 1.0},
        }
    
    def compose(self) -> ComposeResult:
        with Container(id="size-container"):
            yield Static("📏 DATASET SIZE", classes="title")
            yield Static("Choose preset:", classes="section-title")
            
            with RadioSet(id="size-preset"):
                yield RadioButton("Small (~1K customers, quick test)", id="preset-small")
                yield RadioButton("Medium (~10K customers, standard)", id="preset-medium", value=True)
                yield RadioButton("Large (~50K customers, production-like)", id="preset-large")
                yield RadioButton("Custom (specify parameters)", id="preset-custom")
            
            yield Static("", id="preset-info", classes="preset-info")
            
            with Horizontal(classes="button-container"):
                yield Button("Continue", variant="primary", id="btn-continue")
                yield Button("Cancel", id="btn-cancel")
    
    def on_mount(self) -> None:
        """Update info on mount"""
        self.update_preset_info("medium")
    
    @on(RadioSet.Changed)
    def handle_preset_change(self, event: RadioSet.Changed) -> None:
        """Handle preset selection change"""
        if event.pressed.id is None:
            return
        preset = event.pressed.id.replace("preset-", "")
        self.update_preset_info(preset)
    
    def update_preset_info(self, preset: str) -> None:
        """Update the preset information display"""
        info_widget = self.query_one("#preset-info", Static)
        
        if preset == "custom":
            info_text = "[yellow]Custom mode:[/yellow] You'll specify all parameters manually"
        else:
            config = self.preset_configs[preset]
            # Calculate estimates
            duration_hours = self._parse_duration_hours(self.scenario_config.duration) * config["duration_mult"]
            est_orders = int(config["orders_per_hour"] * duration_hours * self.scenario_config.intensity_multiplier)
            
            info_text = f"""[bold]Auto-calculated for {preset.upper()} preset:[/bold]
  Customers: {config['customers']:,}
  Duration: {self._format_duration(duration_hours)}
  Intensity: {self.scenario_config.intensity_multiplier}x
  Est. Orders: {est_orders:,}
  Est. Support Tickets: ~{int(est_orders * 0.12):,}
"""
        
        info_widget.update(info_text)
    
    def _parse_duration_hours(self, duration_str: str) -> float:
        """Parse duration string to hours"""
        if duration_str.endswith('h'):
            return float(duration_str[:-1])
        elif duration_str.endswith('d'):
            return float(duration_str[:-1]) * 24
        else:
            return 24.0
    
    def _format_duration(self, hours: float) -> str:
        """Format hours into readable duration"""
        if hours < 24:
            return f"{hours:.1f}h"
        else:
            days = hours / 24
            return f"{days:.1f}d"
    
    def action_cancel(self) -> None:
        """Go back to scenario selection"""
        self.app.pop_screen()
    
    @on(Button.Pressed, "#btn-cancel")
    def handle_cancel(self) -> None:
        """Handle cancel button"""
        self.action_cancel()
    
    @on(Button.Pressed, "#btn-continue")
    def handle_continue(self) -> None:
        """Handle continue button"""
        radio_set = self.query_one("#size-preset", RadioSet)
        selected = radio_set.pressed_button
        
        if selected and selected.id is not None:
            preset = selected.id.replace("preset-", "")
            
            if preset == "custom":
                self.app.push_screen(CustomParametersScreen(self.scenario_name, self.scenario_config))
            else:
                # Apply preset configuration
                config = self.preset_configs[preset]
                updated_config = ScenarioConfig(
                    name=self.scenario_config.name,
                    duration=self.scenario_config.duration,
                    intensity_multiplier=self.scenario_config.intensity_multiplier,
                    correlations=self.scenario_config.correlations,
                    special_params={
                        **(self.scenario_config.special_params or {}),
                        "customers": config["customers"],
                        "orders_per_hour": config["orders_per_hour"]
                    }
                )
                
                # Move to confirmation
                self.app.push_screen(ConfirmationScreen(self.scenario_name, updated_config, preset))


class CustomParametersScreen(Screen):
    """Custom parameter input screen"""
    
    BINDINGS = [
        Binding("escape", "cancel", "Back", show=True),
    ]
    
    CSS = """
    CustomParametersScreen {
        align: center middle;
    }
    
    #params-container {
        width: 80;
        height: auto;
        border: heavy $primary;
        background: $surface;
        padding: 2;
    }
    
    .title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 2;
    }
    
    .input-group {
        margin: 1 0;
    }
    
    .input-label {
        color: $text;
        margin-bottom: 0;
    }
    
    Input {
        width: 100%;
    }
    
    .button-container {
        layout: horizontal;
        align: center middle;
        margin-top: 2;
    }
    
    Button {
        margin: 0 1;
    }
    """
    
    def __init__(self, scenario_name: str, scenario_config: ScenarioConfig):
        super().__init__()
        self.scenario_name = scenario_name
        self.scenario_config = scenario_config
    
    def compose(self) -> ComposeResult:
        with ScrollableContainer(id="params-container"):
            yield Static("⚙️  CUSTOM PARAMETERS", classes="title")
            
            with Vertical(classes="input-group"):
                yield Label("Number of Customers:", classes="input-label")
                yield Input(placeholder="e.g., 15000", id="input-customers", value="15000")
            
            with Vertical(classes="input-group"):
                yield Label("Orders Per Hour:", classes="input-label")
                yield Input(placeholder="e.g., 800", id="input-orders-per-hour", value="800")
            
            with Vertical(classes="input-group"):
                yield Label("Duration (e.g., 4h, 14d, 30m):", classes="input-label")
                yield Input(placeholder="e.g., 24h", id="input-duration", 
                          value=self.scenario_config.duration)
            
            with Vertical(classes="input-group"):
                yield Label("Intensity Multiplier:", classes="input-label")
                yield Input(placeholder="e.g., 1.5", id="input-intensity",
                          value=str(self.scenario_config.intensity_multiplier))
            
            if self.scenario_name == "flash_sale":
                with Vertical(classes="input-group"):
                    yield Label("Discount Percentage:", classes="input-label")
                    yield Input(placeholder="e.g., 50", id="input-discount", value="50")
                
                with Vertical(classes="input-group"):
                    yield Label("Target Category:", classes="input-label")
                    yield Input(placeholder="e.g., electronics", id="input-category", 
                              value="electronics")
            
            with Horizontal(classes="button-container"):
                yield Button("Continue", variant="primary", id="btn-continue")
                yield Button("Cancel", id="btn-cancel")
    
    def action_cancel(self) -> None:
        """Go back"""
        self.app.pop_screen()
    
    @on(Button.Pressed, "#btn-cancel")
    def handle_cancel(self) -> None:
        """Handle cancel button"""
        self.action_cancel()
    
    @on(Button.Pressed, "#btn-continue")
    def handle_continue(self) -> None:
        """Handle continue button - validate and proceed"""
        try:
            customers = int(self.query_one("#input-customers", Input).value)
            orders_per_hour = int(self.query_one("#input-orders-per-hour", Input).value)
            duration = self.query_one("#input-duration", Input).value
            intensity = float(self.query_one("#input-intensity", Input).value)
            
            # Build special params
            special_params = {
                "customers": customers,
                "orders_per_hour": orders_per_hour,
            }

            # Add scenario-specific params
            if self.scenario_name == "flash_sale":
                discount = int(self.query_one("#input-discount", Input).value)
                category = self.query_one("#input-category", Input).value
                special_params["discount"] = discount
                # Convert category to a numeric representation to avoid type conflicts
                special_params["category"] = category_mapping(category.lower())  # Use numeric representation
            
            # Create updated config
            updated_config = ScenarioConfig(
                name=self.scenario_config.name,
                duration=duration,
                intensity_multiplier=intensity,
                correlations=self.scenario_config.correlations,
                special_params=special_params
            )
            
            # Move to confirmation
            self.app.push_screen(ConfirmationScreen(self.scenario_name, updated_config, "custom"))
            
        except ValueError as e:
            # Show error message
            self.notify(f"Invalid input: {e}", severity="error", timeout=3)


class CustomScenarioScreen(Screen):
    """Custom scenario builder"""
    
    BINDINGS = [
        Binding("escape", "cancel", "Back", show=True),
    ]
    
    CSS = """
    CustomScenarioScreen {
        align: center middle;
    }
    
    #custom-container {
        width: 80;
        height: auto;
        border: heavy $primary;
        background: $surface;
        padding: 2;
    }
    
    .title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 2;
    }
    
    .input-group {
        margin: 1 0;
    }
    
    .input-label {
        color: $text;
        margin-bottom: 0;
    }
    
    Input {
        width: 100%;
    }
    
    .button-container {
        layout: horizontal;
        align: center middle;
        margin-top: 2;
    }
    
    Button {
        margin: 0 1;
    }
    """
    
    def compose(self) -> ComposeResult:
        with ScrollableContainer(id="custom-container"):
            yield Static("🛠️  BUILD CUSTOM SCENARIO", classes="title")
            
            with Vertical(classes="input-group"):
                yield Label("Scenario Name:", classes="input-label")
                yield Input(placeholder="e.g., my_custom_scenario", id="input-name")
            
            with Vertical(classes="input-group"):
                yield Label("Duration (e.g., 4h, 14d):", classes="input-label")
                yield Input(placeholder="e.g., 24h", id="input-duration", value="24h")
            
            with Vertical(classes="input-group"):
                yield Label("Intensity Multiplier:", classes="input-label")
                yield Input(placeholder="e.g., 1.5", id="input-intensity", value="1.0")
            
            with Vertical(classes="input-group"):
                yield Label("Number of Customers:", classes="input-label")
                yield Input(placeholder="e.g., 15000", id="input-customers", value="15000")
            
            with Vertical(classes="input-group"):
                yield Label("Orders Per Hour:", classes="input-label")
                yield Input(placeholder="e.g., 800", id="input-orders-per-hour", value="800")
            
            with Horizontal(classes="button-container"):
                yield Button("Continue", variant="primary", id="btn-continue")
                yield Button("Cancel", id="btn-cancel")
    
    def action_cancel(self) -> None:
        """Go back"""
        self.app.pop_screen()
    
    @on(Button.Pressed, "#btn-cancel")
    def handle_cancel(self) -> None:
        """Handle cancel button"""
        self.action_cancel()
    
    @on(Button.Pressed, "#btn-continue")
    def handle_continue(self) -> None:
        """Handle continue button"""
        try:
            name = self.query_one("#input-name", Input).value
            duration = self.query_one("#input-duration", Input).value
            intensity = float(self.query_one("#input-intensity", Input).value)
            customers = int(self.query_one("#input-customers", Input).value)
            orders_per_hour = int(self.query_one("#input-orders-per-hour", Input).value)
            
            if not name:
                self.notify("Please enter a scenario name", severity="warning", timeout=3)
                return
            
            # Create custom config
            custom_config = ScenarioConfig(
                name=name,
                duration=duration,
                intensity_multiplier=intensity,
                special_params={
                    "customers": customers,
                    "orders_per_hour": orders_per_hour
                }
            )
            
            # Move to confirmation
            self.app.push_screen(ConfirmationScreen(name, custom_config, "custom"))
            
        except ValueError as e:
            self.notify(f"Invalid input: {e}", severity="error", timeout=3)


class ConfirmationScreen(Screen):
    """Final confirmation before generation"""
    
    BINDINGS = [
        Binding("escape", "cancel", "Back", show=True),
    ]
    
    CSS = """
    ConfirmationScreen {
        align: center middle;
    }
    
    #confirm-container {
        width: 80;
        height: auto;
        border: heavy $primary;
        background: $surface;
        padding: 2;
    }
    
    .title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 2;
    }
    
    .summary {
        background: $boost;
        padding: 1;
        margin: 1 0;
        border: solid $primary;
    }

    .input-group {
        margin: 1 0;
    }

    .input-label {
        color: $text;
        margin-bottom: 0;
    }

    Input {
        width: 100%;
    }

    .warning {
        color: $warning;
        text-align: center;
        margin: 1 0;
    }
    
    .button-container {
        layout: horizontal;
        align: center middle;
        margin-top: 2;
    }
    
    Button {
        margin: 0 1;
    }
    """
    
    def __init__(self, scenario_name: str, scenario_config: ScenarioConfig, preset: str):
        super().__init__()
        self.scenario_name = scenario_name
        self.scenario_config = scenario_config
        self.preset = preset
    
    def compose(self) -> ComposeResult:
        with Container(id="confirm-container"):
            yield Static("✅ CONFIRM GENERATION", classes="title")
            
            summary_text = self._build_summary()
            yield Static(summary_text, classes="summary", markup=True)

            with Vertical(classes="input-group"):
                yield Label("Output Directory (relative to data/):", classes="input-label")
                yield Input(placeholder="e.g., custom_scenario", id="input-output-dir", value="")

            yield Static("⚠️  This will generate data files in the ./data directory (or custom subdirectory if specified)", classes="warning")
            
            with Horizontal(classes="button-container"):
                yield Button("Generate Data", variant="success", id="btn-generate")
                yield Button("Cancel", id="btn-cancel")
    
    def _build_summary(self) -> str:
        """Build confirmation summary"""
        special_params = self.scenario_config.special_params or {}
        
        # Calculate estimates
        duration_hours = self._parse_duration_hours(self.scenario_config.duration)
        orders_per_hour = special_params.get("orders_per_hour", 800)
        est_orders = int(duration_hours * orders_per_hour * self.scenario_config.intensity_multiplier)
        
        summary = f"""[bold cyan]Scenario:[/bold cyan] {self.scenario_name.replace('_', ' ').title()}
[bold cyan]Preset:[/bold cyan] {self.preset.upper()}

[bold]Configuration:[/bold]
  • Duration: {self.scenario_config.duration}
  • Intensity: {self.scenario_config.intensity_multiplier}x
  • Customers: {special_params.get('customers', 15000):,}
  • Orders/Hour: {orders_per_hour:,}

[bold]Estimates:[/bold]
  • Total Orders: ~{est_orders:,}
  • Support Tickets: ~{int(est_orders * 0.12):,}
  • Cart Abandonments: ~{int(est_orders * 0.25):,}
  • Returns: ~{int(est_orders * 0.08):,}
"""
        
        if special_params:
            summary += "\n[bold]Special Parameters:[/bold]\n"
            for key, value in special_params.items():
                if key not in ["customers", "orders_per_hour"]:
                    summary += f"  • {key}: {value}\n"
        
        return summary
    
    def _parse_duration_hours(self, duration_str: str) -> float:
        """Parse duration string to hours"""
        if duration_str.endswith('h'):
            return float(duration_str[:-1])
        elif duration_str.endswith('d'):
            return float(duration_str[:-1]) * 24
        else:
            return 24.0
    
    def action_cancel(self) -> None:
        """Go back"""
        self.app.pop_screen()
    
    @on(Button.Pressed, "#btn-cancel")
    def handle_cancel(self) -> None:
        """Handle cancel button"""
        self.action_cancel()
    
    @on(Button.Pressed, "#btn-generate")
    def handle_generate(self) -> None:
        """Start data generation"""
        # Get custom output directory if specified
        output_dir_input = self.query_one("#input-output-dir", Input)
        custom_subdir = output_dir_input.value.strip() if output_dir_input else ""

        # Create full output directory path
        if custom_subdir:
            output_dir = f"data/{custom_subdir}"
        else:
            output_dir = "data"

        self.app.push_screen(GenerationScreen(self.scenario_name, self.scenario_config, output_dir))


class GenerationScreen(Screen):
    """Data generation progress screen"""
    
    CSS = """
    GenerationScreen {
        align: center middle;
    }
    
    #generation-container {
        width: 80;
        height: auto;
        border: heavy $primary;
        background: $surface;
        padding: 2;
    }
    
    .title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 2;
    }
    
    .status {
        text-align: center;
        margin: 1 0;
    }
    
    .log {
        height: 20;
        background: $panel;
        padding: 1;
        margin: 1 0;
        border: solid $primary;
    }
    
    .complete {
        text-align: center;
        color: $success;
        text-style: bold;
        margin: 2 0;
    }
    
    .button-container {
        layout: horizontal;
        align: center middle;
        margin-top: 2;
    }
    """
    
    def __init__(self, scenario_name: str, scenario_config: ScenarioConfig, output_dir: str = "data"):
        super().__init__()
        self.scenario_name = scenario_name
        self.scenario_config = scenario_config
        self.output_dir = output_dir
        self.generator = None
    
    def compose(self) -> ComposeResult:
        with Container(id="generation-container"):
            yield Static("⚙️  GENERATING DATA", classes="title")
            yield ProgressBar(total=100, show_eta=False, id="progress")
            yield Static("Initializing...", id="status", classes="status")
            yield ScrollableContainer(
                Static("", id="log-content"),
                classes="log"
            )
            yield Static("", id="complete-message", classes="complete")
            with Horizontal(classes="button-container"):
                yield Button("Done", variant="primary", id="btn-done", disabled=True)
    
    async def on_mount(self) -> None:
        """Start generation when screen mounts"""
        await self.generate_data()
    
    async def generate_data(self) -> None:
        """Run the data generation process"""
        progress = self.query_one("#progress", ProgressBar)
        status = self.query_one("#status", Static)
        log_content = self.query_one("#log-content", Static)
        complete_msg = self.query_one("#complete-message", Static)
        done_btn = self.query_one("#btn-done", Button)
        
        try:
            # Initialize generator
            status.update("🚀 Initializing generator...")
            self.add_log("Starting synthetic data generation...")
            await asyncio.sleep(0.5)

            # Ensure output directory exists
            output_path = Path(self.output_dir)
            if not output_path.exists():
                output_path.mkdir(parents=True, exist_ok=True)
                self.add_log(f"Created output directory: {self.output_dir}")

            self.generator = SyntheticDataGenerator(
                output_dir=self.output_dir,
                output_format="csv"
            )
            progress.update(progress=10)
            
            # Generate customers
            status.update("👥 Generating customers...")
            special_params = self.scenario_config.special_params or {}
            customers_count = special_params.get('customers', 15000)
            self.add_log(f"Generating {customers_count} customers...")
            await asyncio.sleep(0.1)
            self.generator.data["customers"] = self.generator.generate_customers(
                customers_count,
                self.scenario_config
            )
            progress.update(progress=20)
            self.add_log(f"✅ Generated {len(self.generator.data['customers'])} customers")
            
            # Generate suppliers
            status.update("🏭 Generating suppliers...")
            self.add_log("Generating suppliers...")
            await asyncio.sleep(0.1)
            self.generator.data["suppliers"] = self.generator.generate_suppliers()
            progress.update(progress=30)
            self.add_log(f"✅ Generated {len(self.generator.data['suppliers'])} suppliers")
            
            # Generate products
            status.update("📦 Generating products...")
            self.add_log("Generating product catalog...")
            await asyncio.sleep(0.1)
            self.generator.data["products"] = self.generator.generate_products(
                self.generator.data["suppliers"],
                self.scenario_config
            )
            progress.update(progress=40)
            self.add_log(f"✅ Generated {len(self.generator.data['products'])} products")
            
            # Generate campaigns
            status.update("🎯 Generating campaigns...")
            self.add_log("Generating marketing campaigns...")
            await asyncio.sleep(0.1)
            self.generator.data["campaigns"] = self.generator.generate_campaigns(self.scenario_config)
            progress.update(progress=45)
            self.add_log(f"✅ Generated {len(self.generator.data['campaigns'])} campaigns")
            
            # Generate orders
            status.update("🛒 Generating orders...")
            self.add_log("Generating order data (this may take a moment)...")
            await asyncio.sleep(0.1)
            self.generator.data["orders"] = self.generator.generate_orders(
                self.generator.data["customers"],
                self.generator.data["products"],
                self.generator.data["campaigns"],
                self.scenario_config
            )
            progress.update(progress=60)
            self.add_log(f"✅ Generated {len(self.generator.data['orders'])} orders")
            
            # Generate support tickets
            status.update("💬 Generating support tickets...")
            self.add_log("Generating support tickets...")
            await asyncio.sleep(0.1)
            self.generator.data["support_tickets"] = self.generator.generate_support_tickets(
                self.generator.data["customers"],
                self.generator.data["orders"],
                self.scenario_config
            )
            progress.update(progress=70)
            self.add_log(f"✅ Generated {len(self.generator.data['support_tickets'])} support tickets")
            
            # Generate cart abandonment
            status.update("🛒 Generating cart abandonments...")
            self.add_log("Generating cart abandonment data...")
            await asyncio.sleep(0.1)
            self.generator.data["cart_abandonment"] = self.generator.generate_cart_abandonment(
                self.generator.data["customers"],
                self.generator.data["products"],
                self.generator.data["orders"],
                self.scenario_config
            )
            progress.update(progress=80)
            self.add_log(f"✅ Generated {len(self.generator.data['cart_abandonment'])} abandonments")
            
            # Generate returns
            status.update("🔄 Generating returns...")
            self.add_log("Generating returns data...")
            await asyncio.sleep(0.1)
            self.generator.data["returns"] = self.generator.generate_returns(
                self.generator.data["orders"],
                self.generator.data["customers"],
                self.generator.data["products"],
                self.scenario_config
            )
            progress.update(progress=90)
            self.add_log(f"✅ Generated {len(self.generator.data['returns'])} returns")
            
            # Generate system metrics
            status.update("📊 Generating system metrics...")
            self.add_log("Generating system metrics...")
            await asyncio.sleep(0.1)
            self.generator.data["system_metrics"] = self.generator.generate_system_metrics(
                self.scenario_config
            )
            progress.update(progress=95)
            self.add_log(f"✅ Generated {len(self.generator.data['system_metrics'])} metrics")
            
            # Save data
            status.update("💾 Saving files...")
            self.add_log("Saving files to disk...")
            await asyncio.sleep(0.1)
            
            tables = [
                "customers", "suppliers", "products", "campaigns", 
                "orders", "order_items", "support_tickets", 
                "cart_abandonment", "returns", "system_metrics"
            ]
            
            saved_files = self.generator.save_data(tables, self.scenario_name)
            progress.update(progress=100)
            
            for filename in saved_files:
                self.add_log(f"💾 Saved: {filename}")
            
            # Complete
            status.update("✅ Generation Complete!")
            complete_msg.update("🎉 Data generation successful!")
            self.add_log("\n✨ All data files generated successfully!")
            self.add_log(f"📁 Files saved to: ./{self.output_dir}/")
            
            done_btn.disabled = False
            
        except Exception as e:
            status.update("❌ Generation Failed")
            complete_msg.update(f"❌ Error: {str(e)}")
            self.add_log(f"\n❌ Error: {str(e)}")
            done_btn.disabled = False
    
    def add_log(self, message: str) -> None:
        """Add message to log"""
        log_content = self.query_one("#log-content", Static)
        current = str(log_content) if hasattr(log_content, 'plain') else str(log_content)
        log_content.update(f"{current}\n{message}" if current else message)
    
    @on(Button.Pressed, "#btn-done")
    def handle_done(self) -> None:
        """Return to main menu"""
        self.app.pop_screen()
        self.app.pop_screen()
        self.app.pop_screen()


class HelpScreen(Screen):
    """Help information screen"""
    
    BINDINGS = [
        Binding("escape", "close", "Close", show=True),
    ]
    
    CSS = """
    HelpScreen {
        align: center middle;
    }
    
    #help-container {
        width: 80;
        height: auto;
        border: heavy $primary;
        background: $surface;
        padding: 2;
    }
    
    .title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 2;
    }
    """
    
    def compose(self) -> ComposeResult:
        with ScrollableContainer(id="help-container"):
            yield Static("❓ HELP", classes="title")
            yield Static("""
[bold cyan]Synthetic E-Commerce Data Generator[/bold cyan]

This tool generates realistic synthetic e-commerce data for testing,
ML training, and business scenario simulation.

[bold]Navigation:[/bold]
  • Use ↑↓ arrow keys or Tab to navigate
  • Press Enter to select
  • Press Escape to go back
  • Press F1 for help (this screen)
  • Press Q to quit

[bold]Scenarios:[/bold]
  • Flash Sale: High-intensity traffic spike (4h)
  • Returns Wave: Post-holiday returns surge (14d)
  • Supply Disruption: Supplier delays (14d)
  • Payment Outage: Payment gateway issues (6h)
  • Viral Moment: TikTok viral traffic (24h)
  • Customer Segments: Cohort analysis (180d)
  • Seasonal Planning: Seasonal campaigns (60d)
  • Multi-Channel: Channel migration (90d)
  • Baseline: Normal operations (30d)
  • Custom: Build your own scenario

[bold]Dataset Sizes:[/bold]
  • Small: ~1K customers, quick test
  • Medium: ~10K customers, standard
  • Large: ~50K customers, production-like
  • Custom: Specify all parameters

[bold]Output:[/bold]
Files are saved to ./data/ directory in CSV format.

Press Escape to close this help screen.
            """, markup=True)
    
    def action_close(self) -> None:
        """Close help screen"""
        self.app.pop_screen()


class DataGeneratorApp(App):
    """Main TUI application"""
    
    CSS = """
    Screen {
        background: $background;
    }
    """
    
    SCREENS = {
        "loading": LoadingScreen,
        "scenario_selection": ScenarioSelectionScreen,
        "help": HelpScreen,
    }
    
    def on_mount(self) -> None:
        """Start with loading screen"""
        self.push_screen("loading")


if __name__ == "__main__":
    app = DataGeneratorApp()
    app.run()