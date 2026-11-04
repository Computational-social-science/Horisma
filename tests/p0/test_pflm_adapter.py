"""Lightweight observer-contract tests; no model weights or torch needed in CI."""
import pytest
from horisma_p0.operators import ContractError
from horisma_p0.pflm_adapter import score_text_bytes,rank_pattern_labels


class ConstantModel:
    def bits_per_byte(self,data,chunk=256):return [8.0]*len(data)
    def stream(self,chunk=256):return self
    def feed(self,data):return [8.0]*len(data)


def test_byte_cost_has_a_denominator_and_no_truth_authority():
    result=score_text_bytes(ConstantModel(),'术语'.encode())
    assert result['byte_count']==6 and result['mean_bits_per_byte']==8
    assert result['scientific_approval_granted'] is False and result['source_modified'] is False


def test_empty_text_is_undefined_not_zero():
    result=score_text_bytes(ConstantModel(),b'')
    assert result['measurement_status']=='NOT_DEFINED' and result['mean_bits_per_byte'] is None


@pytest.mark.parametrize('text',[b'%PDF-1.7',b'\xff'])
def test_binary_input_is_rejected(text):
    with pytest.raises(ContractError):score_text_bytes(ConstantModel(),text)


def test_nonfinite_output_is_not_silently_clamped():
    class Bad(ConstantModel):
        def bits_per_byte(self,data,chunk=256):return [float('nan')]*len(data)
    with pytest.raises(ContractError,match='INVALID_BYTE_SCORE'):score_text_bytes(Bad(),b'x')


def test_label_rank_does_not_authorize_filtering_or_entailment():
    result=rank_pattern_labels(ConstantModel(),b'Explicit synthetic pattern context.',(b'0',b'1'))
    assert result['calibrated_probability'] is None
    assert result['automatic_exclusion_authorized'] is False and result['evidence_support_decision'] is None
    assert result['preferred_label'] is None and result['top_labels_tied']


def test_different_label_lengths_are_not_silently_compared():
    with pytest.raises(ContractError,match='PATTERN_LABEL_LENGTH_MISMATCH'):
        rank_pattern_labels(ConstantModel(),b'context',(b'a',b'long'))


def test_unrelated_metadata_cannot_claim_verified_model_binding():
    model=ConstantModel();model.horisma_pflm_provenance={'unrelated':'not a binding'}
    result=score_text_bytes(model,b'x')
    assert result['model_binding_verified'] is False and result['weights_revision'] is None


def test_single_byte_labels_reuse_prefix_and_preserve_small_top_cost():
    class Peaked(ConstantModel):
        def __init__(self):self.feed_calls=0
        def feed(self,data):self.feed_calls+=1;return super().feed(data)
        def next_byte_logits(self):
            values=[0.0]*256;values[ord('A')]=100.0;return values
    model=Peaked()
    result=rank_pattern_labels(model,b'context',(b'A',b'N'))
    assert result['preferred_label']=='A' and model.feed_calls==1
    assert 0<result['label_costs'][0]['conditional_total_bits']<1e-30
    assert result['prefix_evaluations']==1
