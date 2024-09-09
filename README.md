# StraddleFinder
#### Video Demo: https://youtu.be/fc7d7w1Yir0
#### Description: A Deribit crypto options analytics tool for straddle strategies.


	  _____ _                 _     _ _      ______ _           _
	 / ____| |               | |   | | |    |  ____(_)         | |
	| (___ | |_ _ __ __ _  __| | __| | | ___| |__   _ _ __   __| | ___ _ __
	 \___ \| __| '__/ _` |/ _` |/ _` | |/ _ \  __| | | '_ \ / _` |/ _ \ '__|
	 ____) | |_| | | |_| | |_| | |_| | |  __/ |    | | | | | |_| |  __/ |
	|_____/ \__|_|  \__,_|\__,_|\__,_|_|\___|_|    |_|_| |_|\__,_|\___|_|



# DISCLAIMER

StraddleFinder is an open-source experimental software, and the author does not take any responsibility for its usage. Users should understand the following:

Cryptocurrency and options trading carries inherent risks, and users should only engage with funds they can afford to lose. StraddleFinder does not provide financial advice, and users should seek guidance from a qualified financial advisor before trading.

Users are solely responsible for managing their risk exposure while using StraddleFinder. This includes implementing appropriate risk management strategies and choosing proper position sizing.

The author of StraddleFinder is not liable for any damages or losses resulting from the use of the software. Users are expected to comply with all applicable laws and regulations governing cryptocurrency and options trading in their respective jurisdictions.

By using StraddleFinder, users acknowledge and accept these terms and agree to use the software at their own risk.



# WHAT IS STRADDLEFINDER?

StraddleFinder is an open-source crypto options analytics tool for the Deribit exchange that does not require any login.
It is based on a hedging strategy, called Long Straddle, which consists in balancing Call and Put options to ensure profit for market movements in either way. Here's a good explanation by Deribit (https://insights.deribit.com/options-course/sections/section-12-strategies-and-combinations/options-course/lectures/lecture-12-8-long-straddle/) which explains the strategy in detail, or scroll to the "How the strategy works" section for a quicker explanation.

StraddleFinder only works on USDC linear options with quote currency settlement (SOL, MATIC, XRP).



# SYSTEM REQUIREMENTS

## Hardware

No system specifications required, a basic system and a normal connection will do.


## Software:

StraddleFinder depends on the 'requests' Python library. You can install this by typing the following command in the terminal:

### to install 'requests':
	pip install requests


# HOW TO USE STRADDLEFINDER

StraddleFinder does not require any input or login, it just retrieves public information from the Deribit API and compares call and put options to calculate the best straddle strategies, sorted by 'Breakeven %' (see next section for an explanation).

### From terminal it looks like this:

	Options list downloaded
	Retrieving options info: 704 of 704
	Finding straddle deals
	69 deals found

	RESULTS:

	Underlying asset: XRP - Expiration (UTC): 05/07/24-08:00 - Total cost: 13.0 USDC
	Strike price: 0.45 - Breakeven Long: 0.463 - Breakeven Short: 0.437 - Breakeven %: +-2.89% - PPP: 34.6% (4.5 USDC)

	Underlying asset: MATIC - Expiration (UTC): 05/07/24-08:00 - Total cost: 17.5 USDC
	Strike price: 0.52 - Breakeven Long: 0.5375 - Breakeven Short: 0.5025 - Breakeven %: +-3.37% - PPP: 29.67% (5.19 USDC)

	Underlying asset: XRP - Expiration (UTC): 05/07/24-08:00 - Total cost: 15.5 USDC
	Strike price: 0.44 - Breakeven Long: 0.4555 - Breakeven Short: 0.4245 - Breakeven %: +-3.52% - PPP: 28.41% (4.4 USDC)

	...



# HOW THE LONG STRADDLE STRATEGY WORKS

The Long Straddle strategy works by opening positions in opposite directions on the same strike price, so to make profit whether the market goes up or down, provided that the move is big enough to cover the premium paid. The long position is a long call option while the short position is a long put option.

Let's analyse a result to explain the calculations:

	Underlying asset: XRP - Expiration (UTC): 05/07/24-08:00 - Total cost: 13.0 USDC
	Strike price: 0.45 - Breakeven Long: 0.463 - Breakeven Short: 0.437 - Breakeven %: +-2.89% - PPP: 34.6% (4.5 USDC)

Underlying asset: is the asset on which the option is based on, it can be MATIC, SOL or XRP as those are the only options settled with quote currency on Deribit.

Expiration: the expiration date and time in UTC format, as Deribit uses the same timezone. You'll need this to find the right option on Deribit

Total cost: it is the sum of the premiums to pay for both call and put option, inclusive of fees. It's also needed to calculate the breakeven. Please mind, the prices on the Deribit platform do not include fees.

Strike price: the strike price for both the call and the put option. If you don't know what this is, you shouldn't trade options. Deribit has a very extensive course on that.

#### PLEASE MIND: because of this strategy consisting of 2 options and therefore 2 premiums to cover, the breakeven calculations are calculated on the total cost rather than on the single premium.

Breakeven Long: is the underlying asset price above which the call option will have covered the total cost and starts to be profitable. It is calculated as strikePrice + (totalCost / sharesPerOption)

Breakeven Short: is the underlying asset price below which the put option will have covered the total cost and starts to be profitable. It is calculated as strikePrice - (totalCost / sharesPerOption)

Breakeven %: how much are the breakeven prices above or below the strike price. It also indicates of much does the underlying asset need to move to be in profit. results are sorted by this metric, lowest to highest, as the smaller the breakeven, the higher the probability to be in profit.

PPP: short for 'Profit Per Percent'. Indicates how much profit will you make for every 1% of underlying asset price move, expressed as percentageOfTotalCost (nominalValue). It is a useful metric to understand which options have the highest profitability in relation to the investment. In the above example, PPP is 4.5 USDC, whic is 34.6% of total cost, so you can expect 4.5 USDC profit for every 1% of underlying price move above the long breakeven or the below short breakeven.


For a detailed explanation of a long straddle you can refer to the Deribit Options course: https://insights.deribit.com/options-course/sections/section-12-strategies-and-combinations/options-course/lectures/lecture-12-8-long-straddle/



# HOW TO BUY ON DERIBIT

1. First go on the options sections and select the base currency (MATIC, SOL or XRP).
2. Click on the desired expiration date on the top left.
3. In the central column there are the strike prices, call options are on the left and put options on the right.
4. Find the desired strike price and double click on the corresponding options you want to buy
