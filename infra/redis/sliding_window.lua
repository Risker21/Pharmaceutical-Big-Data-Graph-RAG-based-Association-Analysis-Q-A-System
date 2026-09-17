local key = KEYS[1]
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local max = tonumber(ARGV[3])
local min_score = now - window
redis.call('ZREMRANGEBYSCORE', key, '-inf', min_score)
local count = redis.call('ZCARD', key)
if count < max then
    redis.call('ZADD', key, now, ARGV[4] or now .. '-' .. math.random(1000000))
    redis.call('EXPIRE', key, math.ceil(window / 1000) + 1)
    return {1, max - count - 1, 0}
else
    local oldest = tonumber(redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')[2] or now)
    local reset_after = (oldest + window) - now
    return {0, 0, reset_after}
end
