"""Testes para métricas de similaridade."""

import pytest
import math
from modules.embeddings.similarity import cosine_similarity, dot_product, euclidean_distance


def test_cosine_identical_vectors():
    v = [1.0, 0.0, 0.0]
    assert cosine_similarity(v, v) == pytest.approx(1.0, abs=1e-6)


def test_cosine_orthogonal_vectors():
    v1 = [1.0, 0.0]
    v2 = [0.0, 1.0]
    assert cosine_similarity(v1, v2) == pytest.approx(0.0, abs=1e-6)


def test_cosine_opposite_vectors():
    v1 = [1.0, 0.0]
    v2 = [-1.0, 0.0]
    assert cosine_similarity(v1, v2) == pytest.approx(-1.0, abs=1e-6)


def test_cosine_symmetry():
    v1 = [0.3, 0.4, 0.5]
    v2 = [0.1, 0.9, 0.2]
    assert cosine_similarity(v1, v2) == pytest.approx(cosine_similarity(v2, v1), abs=1e-6)


def test_dot_product_normalized():
    v = [1.0, 0.0, 0.0]
    assert dot_product(v, v) == pytest.approx(1.0, abs=1e-6)


def test_euclidean_same_point():
    v = [1.0, 2.0, 3.0]
    assert euclidean_distance(v, v) == pytest.approx(0.0, abs=1e-6)


def test_euclidean_distance():
    v1 = [0.0, 0.0]
    v2 = [3.0, 4.0]
    assert euclidean_distance(v1, v2) == pytest.approx(5.0, abs=1e-6)
