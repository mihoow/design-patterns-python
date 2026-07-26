"""Run the interactive SSH file transfer example."""

from pathlib import Path

from .ssh_file_transfer import send_file_to_local_pc


if __name__ == "__main__":
    remote_username = input("Username on the destination PC: ")
    remote_ip_address = input(
        "IP address of the destination PC on the local network: "
    )
    output_filename = input("Output filename on the destination PC: ")

    send_file_to_local_pc(
        username=remote_username,
        ip_address=remote_ip_address,
        input_path=Path(__file__).resolve().parent / "input.txt",
        output_filename=output_filename,
    )
