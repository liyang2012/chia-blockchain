import atexit
import pytest
import pytest_asyncio
import tempfile
from pathlib import Path
from chia.consensus.constants import ConsensusConstants
from tests.block_tools import BlockTools, test_constants, create_block_tools
from tests.util.keyring import TempKeyring
from typing import Tuple


def cleanup_keyring(keyring: TempKeyring):
    keyring.cleanup()


temp_keyring = TempKeyring(populate=True)
keychain = temp_keyring.get_keychain()
atexit.register(cleanup_keyring, temp_keyring)  # Attempt to clean up the temp keychain


@pytest.fixture(scope="session", name="bt")
def bt() -> BlockTools:
    _shared_block_tools = create_block_tools(constants=test_constants, keychain=keychain)
    return _shared_block_tools
    # yield _shared_block_tools
    # _shared_block_tools.cleanup()


@pytest.fixture(scope="session")
def self_hostname(bt):
    return bt.config["self_hostname"]


def setup_shared_block_tools_and_keyring(
    consensus_constants: ConsensusConstants = test_constants,
) -> Tuple[BlockTools, TempKeyring]:
    temp_keyring = TempKeyring(populate=True)
    bt = create_block_tools(constants=consensus_constants, keychain=temp_keyring.get_keychain())
    return bt, temp_keyring


@pytest_asyncio.fixture(scope="function", params=[1, 2])
async def empty_blockchain(request):
    """
    Provides a list of 10 valid blocks, as well as a blockchain with 9 blocks added to it.
    """
    from tests.util.blockchain import create_blockchain
    from tests.setup_nodes import test_constants

    bc1, connection, db_path = await create_blockchain(test_constants, request.param)
    yield bc1

    await connection.close()
    bc1.shut_down()
    db_path.unlink()


@pytest.fixture(scope="function", params=[1, 2])
def db_version(request):
    return request.param


@pytest.fixture(scope="function", params=[1000000, 2300000])
def softfork_height(request):
    return request.param


block_format_version = "rc4"


@pytest_asyncio.fixture(scope="session")
async def default_400_blocks(bt):
    from tests.util.blockchain import persistent_blocks

    return persistent_blocks(400, f"test_blocks_400_{block_format_version}.db", bt, seed=b"alternate2")


@pytest_asyncio.fixture(scope="session")
async def default_1000_blocks(bt):
    from tests.util.blockchain import persistent_blocks

    return persistent_blocks(1000, f"test_blocks_1000_{block_format_version}.db", bt)


@pytest_asyncio.fixture(scope="session")
async def pre_genesis_empty_slots_1000_blocks(bt):
    from tests.util.blockchain import persistent_blocks

    return persistent_blocks(
        1000, f"pre_genesis_empty_slots_1000_blocks{block_format_version}.db", bt, seed=b"alternate2", empty_sub_slots=1
    )


@pytest_asyncio.fixture(scope="session")
async def default_10000_blocks(bt):
    from tests.util.blockchain import persistent_blocks

    return persistent_blocks(10000, f"test_blocks_10000_{block_format_version}.db", bt)


@pytest_asyncio.fixture(scope="session")
async def default_20000_blocks(bt):
    from tests.util.blockchain import persistent_blocks

    return persistent_blocks(20000, f"test_blocks_20000_{block_format_version}.db", bt)


@pytest_asyncio.fixture(scope="session")
async def default_10000_blocks_compact(bt):
    from tests.util.blockchain import persistent_blocks

    return persistent_blocks(
        10000,
        f"test_blocks_10000_compact_{block_format_version}.db",
        bt,
        normalized_to_identity_cc_eos=True,
        normalized_to_identity_icc_eos=True,
        normalized_to_identity_cc_ip=True,
        normalized_to_identity_cc_sp=True,
    )


@pytest_asyncio.fixture(scope="function")
async def tmp_dir():
    with tempfile.TemporaryDirectory() as folder:
        yield Path(folder)
