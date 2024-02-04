-- MiniFace module for PES 2021
-- Custom content is used, not LiveCPK/game: content\miniface_server is the root
-- Idea and based on: MiniFace Module by Hawke, 2021
-- Author: Mohamed2746, 2024
-- version: 1.0
-- originally posted on evo-web & github

local fileroot = ".\\content\\miniface-server"
local map_teams
local final_file

local function has_value(tab, val)
	for index, value in ipairs(tab) do
		if value == val then
			return true
		end
	end
	return false
end

local function make_key(ctx, filename)
	if string.match(filename, "common\\render\\symbol\\player") then
		local home = tostring(ctx.home_team)
		local away = tostring(ctx.away_team)

		local miniface_file = filename:match("^.+[/\\](.+)$")
		local player_id = miniface_file:sub(0, #miniface_file - 4)
		local teams = {}

		map_teams = io.open(string.format("%s\\%s\\%s", fileroot, player_id, "map_teams.csv"), "r")
		if map_teams then
			for i in map_teams:lines() do
				table.insert(teams, tostring(i))
			end
			map_teams:close()
			if has_value(teams, home) or has_value(teams, away) then
				for i, team_id in ipairs(teams) do
					-- if team_id == current_team_loading then
					if team_id == home or team_id == away then
						local map_ids =
							io.open(string.format("%s\\%s\\%s\\%s", fileroot, player_id, team_id, "map_ids.csv"), "r")
						if map_ids then
							math.randomseed(os.time())
							local minifaces = {}
							for team in map_ids:lines() do
								table.insert(minifaces, team)
							end
							final_file = string.format(
								"%s\\%s\\%s",
								player_id,
								team_id,
								minifaces[math.random(1, #minifaces)] .. ".dds"
							)
							map_ids:close()
							return final_file
						else
							final_file = filename
						end
					end
				end
			else
				local team_id = teams[math.random(1, #teams)]
				local map_ids =
					io.open(string.format("%s\\%s\\%s\\%s", fileroot, player_id, team_id, "map_ids.csv"), "r")
				if map_ids then
					math.randomseed(os.time())
					local minifaces = {}
					for team in map_ids:lines() do
						table.insert(minifaces, team)
					end
					final_file =
						string.format("%s\\%s\\%s", player_id, team_id, minifaces[math.random(1, #minifaces)] .. ".dds")
					return final_file
				else
					final_file = filename
				end
			end
		else
			final_file = filename
		end
		return final_file
	end
end

local function get_filepath(ctx, filename, key)
	if key and map_teams and string.match(filename, "common\\render\\symbol\\player") then
		return string.format("%s\\%s", fileroot, final_file)
	end
end

local function set_teams()
	map_teams = nil
	final_file = nil
end

local function init(ctx)
	if fileroot:sub(1, 1) == "." then
		fileroot = ctx.sider_dir .. fileroot
	end
	ctx.register("set_teams", set_teams)
	ctx.register("livecpk_make_key", make_key)
	ctx.register("livecpk_get_filepath", get_filepath)
end

return { init = init }
