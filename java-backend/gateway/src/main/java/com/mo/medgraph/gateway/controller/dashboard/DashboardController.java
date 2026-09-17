package com.mo.medgraph.gateway.controller.dashboard;

import com.mo.medgraph.common.result.R;
import org.springframework.web.bind.annotation.*;
import java.util.*;

@RestController
@RequestMapping("/api/v1/dashboard")
@CrossOrigin(origins = "*")
public class DashboardController {

    @GetMapping("/metrics")
    public R<Map<String, Object>> getMetrics() {
        Map<String, Object> data = new HashMap<>();
        data.put("total_drugs", 28450);
        data.put("total_relations", 142300);
        data.put("total_diseases", 1250);
        data.put("total_guidelines", 1050);
        
        List<Map<String, Object>> topContra = new ArrayList<>();
        topContra.add(Map.of("pair", List.of("阿司匹林", "华法林"), "risk_level", "High", "case_count", 1240, "risk_detail", "两类均影响凝血，联用出血事件升高 2~3 倍"));
        topContra.add(Map.of("pair", List.of("左氧氟沙星", "茶碱"), "risk_level", "High", "case_count", 890, "risk_detail", "抑制茶碱代谢，血药浓度升高致心律失常"));
        topContra.add(Map.of("pair", List.of("布洛芬", "华法林"), "risk_level", "High", "case_count", 780, "risk_detail", "胃黏膜损伤叠加抗凝，消化道大出血"));
        topContra.add(Map.of("pair", List.of("卡托普利", "螺内酯"), "risk_level", "Medium", "case_count", 410, "risk_detail", "RAAS协同升血钾，警惕高钾血症"));
        topContra.add(Map.of("pair", List.of("辛伐他汀", "奥美拉唑"), "risk_level", "Medium", "case_count", 320, "risk_detail", "CYP3A4代谢干扰，肌痛风险增加"));
        data.put("top_contraindications", topContra);
        
        List<Map<String, Object>> deptDist = new ArrayList<>();
        deptDist.add(Map.of("department", "心内科", "count", 4200));
        deptDist.add(Map.of("department", "呼吸内科", "count", 3800));
        deptDist.add(Map.of("department", "内分泌科", "count", 3500));
        deptDist.add(Map.of("department", "消化内科", "count", 2900));
        deptDist.add(Map.of("department", "神经内科", "count", 2400));
        deptDist.add(Map.of("department", "骨科/风湿", "count", 1800));
        deptDist.add(Map.of("department", "全科", "count", 1500));
        data.put("department_disease_distribution", deptDist);

        data.put("health_status", Map.of(
            "crawler", "GREEN",
            "etl", "GREEN",
            "graph", "GREEN",
            "ai", "GREEN",
            "rate_limit", "GREEN"
        ));

        return R.ok(data);
    }
}
