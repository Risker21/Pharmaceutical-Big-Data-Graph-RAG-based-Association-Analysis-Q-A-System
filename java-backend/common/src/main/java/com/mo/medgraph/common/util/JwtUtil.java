package com.mo.medgraph.common.util;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.security.Keys;
import jakarta.annotation.PostConstruct;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.*;

@Component
public class JwtUtil {

    private static final String DEFAULT_SECRET = "MedGraphRAG-Super-Secret-Key-Please-Change-In-Prod-0123456789";
    private static String staticSecret = DEFAULT_SECRET;
    private static long staticExpireHours = 12;

    @Value("${jwt.secret:MedGraphRAG-Super-Secret-Key-Please-Change-In-Prod-0123456789}")
    private String secret;

    @Value("${jwt.expire-hours:12}")
    private long expireHours;

    @PostConstruct
    public void init() {
        if (secret != null && !secret.isEmpty()) {
            staticSecret = secret;
        }
        if (expireHours > 0) {
            staticExpireHours = expireHours;
        }
    }

    private static SecretKey getSigningKey(String s) {
        byte[] keyBytes = (s != null ? s : DEFAULT_SECRET).getBytes(StandardCharsets.UTF_8);
        if (keyBytes.length < 32) {
            keyBytes = Arrays.copyOf(keyBytes, 64);
        }
        return Keys.hmacShaKeyFor(keyBytes);
    }

    public static String generateToken(String username, List<String> roles) {
        return generateToken(1L, username, roles);
    }

    public static String generateToken(Long userId, String username, List<String> roles) {
        Date now = new Date();
        Date expiryDate = new Date(now.getTime() + staticExpireHours * 3600 * 1000);
        Map<String, Object> claims = new HashMap<>();
        claims.put("userId", userId);
        claims.put("username", username);
        claims.put("roles", roles);
        return Jwts.builder()
                .setClaims(claims)
                .setSubject(username)
                .setIssuedAt(now)
                .setExpiration(expiryDate)
                .signWith(getSigningKey(staticSecret), SignatureAlgorithm.HS256)
                .compact();
    }

    public static Claims parseToken(String token) {
        return Jwts.parserBuilder()
                .setSigningKey(getSigningKey(staticSecret))
                .build()
                .parseClaimsJws(token)
                .getBody();
    }

    public static String getUsername(String token) {
        return parseToken(token).getSubject();
    }

    public static Long getUserId(String token) {
        Object uid = parseToken(token).get("userId");
        return uid != null ? Long.valueOf(uid.toString()) : null;
    }

    @SuppressWarnings("unchecked")
    public static List<String> getRoles(String token) {
        Object roles = parseToken(token).get("roles");
        return roles instanceof List ? (List<String>) roles : Collections.emptyList();
    }

    public static boolean validateToken(String token) {
        try {
            parseToken(token);
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    public static boolean isTokenExpired(String token) {
        try {
            Date expiration = parseToken(token).getExpiration();
            return expiration.before(new Date());
        } catch (Exception e) {
            return true;
        }
    }
}
