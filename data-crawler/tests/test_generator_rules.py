import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from generator.drug_generator import run_generate_drugs
from generator.disease_generator import run_generate_diseases
from generator.guideline_generator import run_generate_guidelines
from generator.interaction_generator import run_generate_interactions


def test_generator_pipeline():
    d = run_generate_drugs()
    dis = run_generate_diseases()
    g = run_generate_guidelines()
    pairs = run_generate_interactions()
    assert len(d) >= 15
    assert len(dis) >= 10
    assert len(g) >= 1000
    assert len(pairs) >= 500
    high_pairs = [k for k, v in pairs.items() if v[0] == "High"]
    assert len(high_pairs) >= 3
    print(f"[OK] drugs={len(d)}, diseases={len(dis)}, guidelines={len(g)}, pairs={len(pairs)} high={len(high_pairs)}")


if __name__ == "__main__":
    test_generator_pipeline()
