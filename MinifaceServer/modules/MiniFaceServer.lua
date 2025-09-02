-- MiniFace module for PES 2021
-- Custom content is used, not LiveCPK/game: content\miniface_server is the root
-- Idea and based on: MiniFace Module by Hawke, 2021
-- Author: Mohamed2746, 2024
-- version: 1.0
-- originally posted on evo-web & github

local fileroot = ".\\content\\miniface-server"

local function has_a_or_b(tab, a, b)
	for index, value in ipairs(tab) do
		if value == a or value == b then
			return index
		end
	end
	return false
end

local function tableIsEmpty(self)
	for _, _ in pairs(self) do
		return false
	end
	return true
end

local function get_folders_in_dir(dir)
	local t = {}
	for name, type in fs.find_files(dir) do
		if type == "dir" and name ~= "." and name ~= ".." then
			table.insert(t, tostring(name))
		end
	end
	return t
end

local function get_files_in_dir(dir, ext)
	local t = {}
	local pattern = ext and "%." .. ext .. "$" or "*"
	for name, type in fs.find_files(dir) do
		if type == "file" and name:match(pattern) then
			table.insert(t, tostring(name))
		end
	end
	return t
end

local function make_key(ctx, filename)
	if string.match(filename, "common\\render\\symbol\\player") then
		local home          = tostring(ctx.home_team)
		local away          = tostring(ctx.away_team)

		local miniface_file = filename:match("^.+[/\\](.+)$")
		local player_id     = miniface_file:sub(0, #miniface_file - 4)

		local teams         = get_folders_in_dir(string.format("%s\\%s\\*", fileroot, player_id))
		if tableIsEmpty(teams) then
			return filename
		end
		-- log(("Found teams for player %s: %s"):format(player_id, table.concat(teams, ", ")))

		math.randomseed(os.time())
		local index = has_a_or_b(teams, home, away) or teams[math.random(1, #teams)]

		local minifaces =
			get_files_in_dir(string.format("%s\\%s\\%s\\*", fileroot, player_id, teams[index]), "dds")
		if tableIsEmpty(minifaces) then
			return filename
		end
		-- log(("Found minifaces for player %s, team %s: %s"):format(player_id, teams[index], table.concat(minifaces, ", ")))

		return string.format(
			"%s\\%s\\%s\\%s",
			fileroot,
			player_id,
			teams[index],
			minifaces[math.random(1, #minifaces)]
		)
	end
end

local function get_filepath(ctx, filename, key)
	if key then
		return key
	end
end

local function init(ctx)
	if fileroot:sub(1, 1) == "." then
		fileroot = ctx.sider_dir .. fileroot
	end
	ctx.register("livecpk_make_key", make_key)
	ctx.register("livecpk_get_filepath", get_filepath)
end

return { init = init }
