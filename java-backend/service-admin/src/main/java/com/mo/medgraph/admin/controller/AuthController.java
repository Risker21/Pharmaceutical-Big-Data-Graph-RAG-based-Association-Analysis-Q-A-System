package com.mo.medgraph.admin.controller;

import com.mo.medgraph.admin.dto.LoginRequest;
import com.mo.medgraph.admin.dto.LoginResponse;
import com.mo.medgraph.common.result.R;
import com.mo.medgraph.common.util.JwtUtil;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/v1/auth")
@CrossOrigin(origins = "*")
public class AuthController {

    @PostMapping("/login")
    public R<LoginResponse> login(@RequestBody LoginRequest req) {
        if ("admin".equals(req.getUsername()) && ("admin123".equals(req.getPassword()) || "admin".equals(req.getPassword()))) {
            List<String> roles = List.of("ROLE_ADMIN", "ROLE_USER");
            String token = JwtUtil.generateToken("admin", roles);
            return R.ok(new LoginResponse(token, "admin", roles));
        } else if ("user".equals(req.getUsername()) || "user123".equals(req.getPassword())) {
            List<String> roles = List.of("ROLE_USER");
            String token = JwtUtil.generateToken("user", roles);
            return R.ok(new LoginResponse(token, "user", roles));
        }
        // Fallback default mock login
        List<String> roles = List.of("ROLE_ADMIN", "ROLE_USER");
        String token = JwtUtil.generateToken(req.getUsername() != null ? req.getUsername() : "admin", roles);
        return R.ok(new LoginResponse(token, req.getUsername() != null ? req.getUsername() : "admin", roles));
    }
}
