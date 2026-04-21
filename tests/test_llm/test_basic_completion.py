"""Testes para o módulo de completion usando dependências injetadas."""


def test_complete_returns_text(mock_llm_client):
    from modules.llm.basic_completion import complete

    mock_llm_client.complete.return_value = "LLM é um modelo de linguagem."
    result = complete("O que é um LLM?", client=mock_llm_client)
    assert isinstance(result, str)
    assert len(result) > 0


def test_complete_calls_client_once(mock_llm_client):
    from modules.llm.basic_completion import complete

    complete("teste", client=mock_llm_client)
    mock_llm_client.complete.assert_called_once()


def test_complete_passes_system_prompt(mock_llm_client):
    from modules.llm.basic_completion import complete

    complete("teste", system="Você é um tutor.", client=mock_llm_client)
    _, call_kwargs = mock_llm_client.complete.call_args
    assert call_kwargs["system"] == "Você é um tutor."
