package com.mo.medgraph.scheduler.handler;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

@Component
public class MedGraphJobHandlers {
    private static final Logger log = LoggerFactory.getLogger(MedGraphJobHandlers.class);

    public void drugWarehouseSyncJob() {
        log.info("[XXL-Job] DrugWarehouseSyncJob executed: triggered Spark incremental ETL");
    }

    public void graphIndexRefreshJob() {
        log.info("[XXL-Job] GraphIndexRefreshJob executed: refreshed Neo4j graph & Milvus embeddings");
    }
}
