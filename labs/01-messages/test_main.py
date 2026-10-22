from anthropic.types import Usage

from main import estimate_cost


def test_cost_counts_input_and_output_at_their_own_prices() -> None:
    usage = Usage(input_tokens=1_000_000, output_tokens=1_000_000)
    assert estimate_cost(usage) == 2.00 + 10.00


def test_cost_counts_cache_tokens_separately() -> None:
    usage = Usage(
        input_tokens=0,
        output_tokens=0,
        cache_creation_input_tokens=1_000_000,
        cache_read_input_tokens=1_000_000,
    )
    assert estimate_cost(usage) == 2.50 + 0.20
