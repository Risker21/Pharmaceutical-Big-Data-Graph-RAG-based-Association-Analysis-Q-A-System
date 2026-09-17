db = db.getSiblingDB(process.env.MONGO_INITDB_DATABASE || 'medgraph');

db.createCollection('chat_session');
db.chat_session.createIndex({ user_id: 1, session_id: 1 }, { unique: true });
db.chat_session.createIndex({ 'messages.created_at': -1 });

db.createCollection('crawler_stats');
db.crawler_stats.createIndex({ spider_name: 1 }, { unique: true });

db.createCollection('etl_job_history');
db.etl_job_history.createIndex({ job_name: 1, start_ts: -1 });
db.etl_job_history.createIndex({ status: 1 });

db.createCollection('analysis_chat_logs');
db.analysis_chat_logs.createIndex({ session_id: 1, day: 1 });
db.analysis_chat_logs.createIndex({ intent: 1 });

db.createCollection('demo_generation_history');
print('[MongoDB init] Collections created');
