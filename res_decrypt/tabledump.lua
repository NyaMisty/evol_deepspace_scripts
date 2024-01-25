function Vector2(x, y)
    return {
        "Vector2", x, y
    }
end
function Vector3(x, y, z)
    return {
        "Vector3", x, y, z
    }
end
function Vector4(x, y, z, q)
    return {
        "Vector4", x, y, z, q
    }
end
if _ENV == nil then
    _ENV = {}
end
_ENV['Vector4'] = Vector4

local dumplua_closure = [[
local closures = {}
local function closure(t) 
  closures[#closures+1] = t
  t[1] = assert(loadstring(t[1]))
  return t[1]
end

for _,t in pairs(closures) do
  for i = 2,#t do 
    debug.setupvalue(t[1], i-1, t[i]) 
  end 
end
]]

local lua_reserved_keywords = {
  'and', 'break', 'do', 'else', 'elseif', 'end', 'false', 'for', 
  'function', 'if', 'in', 'local', 'nil', 'not', 'or', 'repeat', 
  'return', 'then', 'true', 'until', 'while' }

local function keys(t)
  local res = {}
  local oktypes = { stringstring = true, numbernumber = true }
  local function cmpfct(a,b)
    if oktypes[type(a)..type(b)] then
      return a < b
    else
      return type(a) < type(b)
    end
  end
  for k in pairs(t) do
    res[#res+1] = k
  end
  table.sort(res, cmpfct)
  return res
end

local c_functions = {}
for _,lib in pairs{'_G', 'string', 'table', 'math', 
    'io', 'os', 'coroutine', 'package', 'debug'} do
  local t = _G[lib] or {}
  lib = lib .. "."
  if lib == "_G." then lib = "" end
  for k,v in pairs(t) do
    if type(v) == 'function' and not pcall(string.dump, v) then
      c_functions[v] = lib..k
    end
  end
end

function DataDumper(value, varname, fastmode, ident)
  local defined, dumplua = {}
  -- Local variables for speed optimization
  local string_format, type, string_dump, string_rep = 
        string.format, type, string.dump, string.rep
  local tostring, pairs, table_concat = 
        tostring, pairs, table.concat
  local keycache, strvalcache, out, closure_cnt = {}, {}, {}, 0
  setmetatable(strvalcache, {__index = function(t,value)
    local res = string_format('%q', value)
    t[value] = res
    return res
  end})
  local fcts = {
    string = function(value) return strvalcache[value] end,
    number = function(value) return value end,
    boolean = function(value) return tostring(value) end,
    ['nil'] = function(value) return 'nil' end,
    ['function'] = function(value) 
      return string_format("loadstring(%q)", string_dump(value)) 
    end,
    userdata = function() error("Cannot dump userdata") end,
    thread = function() error("Cannot dump threads") end,
  }
  local function test_defined(value, path)
    if false and defined[value] then
      if path:match("^getmetatable.*%)$") then
        out[#out+1] = string_format("s%s, %s)\n", path:sub(2,-2), defined[value])
      else
        out[#out+1] = path .. " = " .. defined[value] .. "\n"
      end
      return true
    end
    defined[value] = path
  end
  local function make_key(t, key)
    local s
    if false and type(key) == 'string' and key:match('^[_%a][_%w]*$') then
      s = key .. "="
    else
      s = "[" .. dumplua(key, 0) .. "]="
    end
    t[key] = s
    return s
  end
  for _,k in ipairs(lua_reserved_keywords) do
    keycache[k] = '["'..k..'"] = '
  end
  if fastmode then 
    fcts.table = function (value)
      -- Table value
      local numidx = 1
      out[#out+1] = "{"
      for key,val in pairs(value) do
        if key == numidx then
          numidx = numidx + 1
        else
          out[#out+1] = keycache[key]
        end
        local str = dumplua(val)
        out[#out+1] = str..","
      end
      if string.sub(out[#out], -1) == "," then
        out[#out] = string.sub(out[#out], 1, -2);
      end
      out[#out+1] = "}"
      return "" 
    end
  else 
    fcts.table = function (value, ident, path)
      if test_defined(value, path) then return "nil" end
      -- Table value
      local sep, str, numidx, totallen = " ", {}, 1, 0
      local meta, metastr = (debug or getfenv()).getmetatable(value)
      if meta then
        ident = ident + 1
        metastr = dumplua(meta, ident, "getmetatable("..path..")")
        totallen = totallen + #metastr + 16
      end

      for _,key in pairs(keys(value)) do
        local val = value[key]
        local s = ""
        local subpath = path or ""
        if #value < 8 and key == numidx then
          subpath = subpath .. "[" .. numidx .. "]"
          numidx = numidx + 1
        else
          s = keycache[key]
          if not s:match "^%[" then subpath = subpath .. "." end
          subpath = subpath .. s:gsub("%s*=%s*$","")
        end
        s = s .. dumplua(val, ident+1, subpath)
        str[#str+1] = s
        totallen = totallen + #s + 2
      end
      if totallen > 80 then
        sep = "\n" .. string_rep("  ", ident+1)
      end
      str = "{"..sep..table_concat(str, ","..sep).." "..sep:sub(1,-3).."}" 
      if meta then
        sep = sep:sub(1,-3)
        return "setmetatable("..sep..str..","..sep..metastr..sep:sub(1,-3)..")"
      end
      return str
    end
    fcts['function'] = function (value, ident, path)
      if test_defined(value, path) then return "nil" end
      if c_functions[value] then
        return c_functions[value]
      elseif debug == nil or debug.getupvalue(value, 1) == nil then
        return string_format("loadstring(%q)", string_dump(value))
      end
      closure_cnt = closure_cnt + 1
      local res = {string.dump(value)}
      for i = 1,math.huge do
        local name, v = debug.getupvalue(value,i)
        if name == nil then break end
        res[i+1] = v
      end
      return "closure " .. dumplua(res, ident, "closures["..closure_cnt.."]")
    end
  end
  function dumplua(value, ident, path)
    return fcts[type(value)](value, ident, path)
  end
  if varname == nil then
    varname = "return "
  elseif varname:match("^[%a_][%w_]*$") then
    varname = varname .. " = "
  end
  if fastmode then
    setmetatable(keycache, {__index = make_key })
    out[1] = varname
    table.insert(out,dumplua(value, 0))
    return table.concat(out)
  else
    setmetatable(keycache, {__index = make_key })
    local items = {}
    for i=1,10 do items[i] = '' end
    items[3] = dumplua(value, ident or 0, "t")
    if closure_cnt > 0 then
      items[1], items[6] = dumplua_closure:match("(.*\n)\n(.*)")
      out[#out+1] = ""
    end
    if #out > 0 then
      items[2], items[4] = "local t = ", "\n"
      items[5] = table.concat(out)
      items[7] = varname .. "t"
    else
      items[2] = varname
    end
    return table.concat(items)
  end
end
print_table = DataDumper



function rebuildTable(tbl, keys, output)
    for keyName, keyInfo in pairs(keys) do
        if type(keyInfo) == "table" then
            -- 嵌套类型
            local dataPath, nestedType = keyInfo[1], keyInfo[2]
            revNestedType = {}
            for k, v in pairs(nestedType) do
                if type(v) == "table" then
                    revNestedType[v[1]] = {k, v}
                else
                    revNestedType[v] = {k, v}
                end
            end
            ----print(print_table(revNestedType))
            --if true then
            --    return 111
            --end

            --print(keyName .. "->".. tostring(dataPath) .. " -> {}")
            if tbl[dataPath] == nil then
                output[keyName] = nil
            else
                
                local isArr = true
                if type(tbl[dataPath][1]) ~= "table" then
                    isArr = false
                elseif tbl[dataPath][1][1] == "Vector2" or tbl[dataPath][1][1] == "Vector3" then
                    isArr = false
                else
                    data = print_table(tbl[dataPath][1])
                    if string.len(data) < 0x1000 then
                        --print("checking arr for ".. print_table(tbl[dataPath][1]) .." vs. " .. print_table(revNestedType))
                    end
                    for k, v in pairs(revNestedType) do
                        if type(v[2]) == "table" and tbl[dataPath][1][k] ~= nil and type(tbl[dataPath][1][k]) ~= "table" then
                            --print("found mismatch on key " .. v[1])
                            isArr = false
                            break
                        end
                    end
                end
                if not isArr then
                    local d = print_table(tbl[dataPath])
                    if string.len(d) < 0x800 then
                        --print("nested type: " .. d)
                    end
                    output[keyName] = {}
                    rebuildTable(tbl[dataPath], nestedType, output[keyName])
                else
                    output[keyName] = {}
                    for i, t in ipairs(tbl[dataPath]) do
                        --print(keyName .. "-> {}[" .. tostring(i) .. "]")
                        local d = print_table(tbl[dataPath][i])
                        if string.len(d) < 0x800 then
                            --print("nested type arr: " .. d)
                        end
                        output[keyName][i] = {}
                        rebuildTable(tbl[dataPath][i], nestedType, output[keyName][i])
                    end
                end
            end
        else
            assert(type(keyInfo) == "number", "KeyInfo必须是整数")
            --print(keyName .. "->" .. tostring(keyInfo) .. "->" .. print_table(tbl[keyInfo]))
            output[keyName] = tbl[keyInfo]
        end
        -- --print("cur output: " .. print_table(output))
    end
    return output
end
function wrapRebuild(tbl)
    local keys = tbl['_k']
    tbl['_k'] = nil
    local output = {}
    local isMultiple = keys['_m'] == true
    keys['_m'] = nil
    for k, v in pairs(tbl) do
        -- print(print_table(v))
        -- print(print_table(keys))
        output[k] = {}
        if isMultiple then
            for i, _ in pairs(v) do
                output[k][i] = rebuildTable(v[i], keys, {})
            end
        else
            output[k] = rebuildTable(v, keys, {})
        end
    end
    output["_schema"] = keys
    output["_schema_is_multiple"] = isMultiple
    return output
end
