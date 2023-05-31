local wezterm = require 'wezterm';

wezterm.on("toggle-alert", function(window, pane)
	local overrides = window:get_config_overrides() or {}
	if not overrides.color_scheme then
		overrides.color_scheme = "Red Alert"
	else
		overrides.color_scheme = nil
	end
	window:set_config_overrides(overrides)
end)

-- font = wezterm.font("IBM Plex Mono", {weight="Regular"}),
return {
  font_size = 15,
  freetype_load_target = "Light",
  color_scheme = "AdventureTime",
  enable_tab_bar = false,
  default_cursor_style = "BlinkingBlock",
  keys = {
    {key="A", mods="CTRL", action=wezterm.action{EmitEvent="toggle-alert"}},
    {key="3", mods="SHIFT", action=wezterm.action{EmitEvent="toggle-alert"}},
  },
}
