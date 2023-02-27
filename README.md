# Bitfinex USD Lending Bot

This application's purpose is to monitor positions and risks by pulling data from the Bitfinex API and displaying it in an easy-to-read way. 

## Features

The Bot includes the following functionalities:

- Upon launching, it sends a P&L snapshot, followed by daily snapshots at 5 pm (London time).
- The daily snapshots include:
  - The amount of money made during the day (based on position modifications, closures, or liquidations).
  - The total amount of money made to date.
  - The amount of USD in active loans, with a percentage of the account.
  - The amount of USD on offer, with a percentage of the account.
  - The amount of USD in the account.
- The command `/B Lending` displays all the current open positions, size, rates, and time left.
- The averages for all the mentioned data points are also displayed.
- The amount is the USD amount, the rate is the daily rate that the lending was filled at, the APR is the rate multiplied by 365, and the time left is the time until the loan expires.

## Background

Bitfinex is a crypto trading platform, similar to Deribit. The project focuses on lending USD in the margin lending platform.

## Instructions

To use the Bot, follow these steps:

1. Clone the repository to your local machine.
2. Install the necessary dependencies using pip.
3. Configure the API keys in the `.env` file.
4. Launch the Bot using `__main__.py`.
5. Use the command `/B Lending` to display the current open positions and their details.

Note: The Bot requires a Bitfinex account and API keys to function properly.

## Contributors

- [Julien Sklarik](https://github.com/Julien-Sklarik)

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).
