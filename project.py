import requests
import sys
import os
import time
from datetime import datetime, timezone

def main():
    # Prints ASCII logo
    printLogo()

    # Assets info
    matic = None #{'indexPrice', 'fees', 'contractSize'}
    sol = None #{'indexPrice', 'fees', 'contractSize'}
    xrp = None #{'indexPrice', 'fees', 'contractSize'}

    # Options databases by asset and type
    maticCalls = [] # [{'name', 'type', 'base','strike', 'ask', 'cost'}]
    maticPuts = [] # [{'name', 'type', 'base','strike', 'ask', 'cost'}]
    solCalls = [] # [{'name', 'type', 'base','strike', 'ask', 'cost'}]
    solPuts = [] # [{'name', 'type', 'base','strike', 'ask', 'cost'}]
    xrpCalls = [] # [{'name', 'type', 'base','strike', 'ask', 'cost'}]
    xrpPuts = [] # [{'name', 'type', 'base','strike', 'ask', 'cost'}]

    # Selected deals database
    deals = [] # {'call', 'put', 'cost', 'strike', 'longBreak', 'shortBreak', 'break%', 'ppp', 'ppp%'}

    # Download asset list
    assetList = requests.get("https://www.deribit.com/api/v2/public/get_instruments", params={"currency": "USDC", "kind": "option"})

    if assetList.status_code != 200:
        # Check response status
        sys.exit("Error:", assetList.status_code, assetList.text)

    print("Options list downloaded")
    assetList = assetList.json()

    counter = 0
    # Retrieve order book for every option
    for asset in assetList['result']:
        counter += 1
        print(f"Retrieving options info: {counter} of {len(assetList['result'])}", end="\r")
        # Avoid overloading server with requests
        while True:
            instrument = requests.get("https://www.deribit.com/api/v2/public/get_order_book", params={"instrument_name": asset['instrument_name']})
            if instrument.status_code != 200:
                time.sleep(0.5)
                continue
            break

        instrument = instrument.json()

        # Check if any sellers on the option
        if instrument['result'] and instrument['result']['asks']:

            #Creates database entries
            strike = float(asset['strike'])
            ask = float(instrument['result']['asks'][0][0])
            optionType = asset['option_type']

            symbolBuffer = {'indexPrice': float(instrument['result']['underlying_price']), 'fees': float(asset['taker_commission']), 'contractSize': int(asset['contract_size'])}
            optionBuffer = {'name': asset['instrument_name'], 'type': optionType, 'base':  asset['base_currency'],'strike': strike, 'ask': float(instrument['result']['asks'][0][0]),
                            'cost': costCalculator(symbolBuffer['fees'], symbolBuffer['indexPrice'], ask, symbolBuffer['contractSize']), 'expiry': asset['expiration_timestamp']}

            # Append database entry to the right database
            match optionBuffer['base']:
                case 'MATIC':
                    if matic == None:
                        matic = symbolBuffer
                    match optionBuffer['type']:
                        case 'call':
                            maticCalls.append(optionBuffer)
                        case 'put':
                            maticPuts.append(optionBuffer)
                case 'SOL':
                    if sol == None:
                        sol = symbolBuffer

                    match optionBuffer['type']:
                        case 'call':
                            solCalls.append(optionBuffer)
                        case 'put':
                            solPuts.append(optionBuffer)
                case 'XRP':
                    if xrp == None:
                        xrp = symbolBuffer

                    match optionBuffer['type']:
                        case 'call':
                            xrpCalls.append(optionBuffer)
                        case 'put':
                            xrpPuts.append(optionBuffer)

    # Compare every call option with every put option for MATIC
    print("\nFinding straddle deals")
    for call in maticCalls:
        for put in maticPuts:
            dealBuffer = dealsCompare(matic, call, put)

            if dealBuffer is not None:
                deals.append(dealBuffer)

    # Compare every call option with every put option for SOL
    for call in solCalls:
        for put in solPuts:
            dealBuffer = dealsCompare(sol, call, put)

            if dealBuffer is not None:
                deals.append(dealBuffer)

    # Compare every call option with every put option for XRP
    for call in xrpCalls:
        for put in xrpPuts:
            dealBuffer = dealsCompare(xrp, call, put)

            if dealBuffer is not None:
                deals.append(dealBuffer)

    # Exiting if no results
    if len(deals) == 0:
        sys.exit("NO DEALS FOUND")

    print(f"{len(deals)} deals found\n\nRESULTS:\n")

    # Sort deals from smallest to largest breakeven as percentage of strike price
    deals = sorted(deals, key=lambda x: x['break%'])


    # Print deals
    for deal in deals:
        expiration = datetime.fromtimestamp(round(deal['expiry']/1000, 0), tz=timezone.utc)
        expiration = expiration.strftime("%d/%m/%y-%H:%M")

        print(f"Underlying asset: {deal['base']} - Expiration (UTC): {expiration} - Total cost: {deal['cost']} USDC")
        print(f"Strike price: {deal['strike']} - Breakeven Long: {deal['longBreak']} - Breakeven Short: {deal['shortBreak']} - Breakeven %: +-{deal['break%']}% - PPP: {deal['ppp%']}% ({deal['ppp']} USDC)\n")


# Print ASCII logo from file
def printLogo():
    logo_path = os.path.join(os.path.dirname(__file__), "logo")

    # Open and print logo file
    try:
        with open(logo_path, "r") as logo_file:
            print(logo_file.read())
    except:
        print("Logo missing!\n")

    return


# Calculates cost per option
def costCalculator(fees, indexPrice, ask, size):
    try:
        fee_per_share = indexPrice*fees
        total_cost = fee_per_share + (ask * size)
        return round(total_cost, 4)
    except:
        raise ValueError("Wrong costCalculator() parameters")


# Calculates breakeven inclusive of fees
def breakevenCalculator(fees, indexPrice, ask, strike, direction):
    try:
        cost_per_share = ask + (fees*indexPrice)
        match direction:
            case 'call':
                return round(strike + cost_per_share, 4)
            case 'put':
                return round(strike - cost_per_share, 4)
            case _:
                raise ValueError("Wrong breakevenCalculator() parameters")
    except:
        raise ValueError("Wrong breakevenCalculator() parameters")


# Calculates the A percentage of B, rounded by R
def percentageCalculator(a, b, r):
    try:
        if a > b:
            raise ValueError("percentageCalculator(a, b, r) - 'a' must be less than 'b'")
        percentage = (a / b) * 100
        return round(percentage, r)
    except:
        raise ValueError("Wrong percentageCalculator() parameters")

# Compares calls and put options
def dealsCompare(asset, call, put):
    if call['strike'] != put['strike'] or call['expiry'] != put['expiry']:
        return None

    totalCost = call['cost'] + put['cost']
    costPerShare = totalCost / asset['contractSize']
    breakPercent = percentageCalculator(costPerShare, call['strike'], 2)
    ppp = percentageCalculator(totalCost/breakPercent, totalCost, 10)


    # Returns a deals database entry
    return {'call': call['name'], 'put': put['name'], 'base': call['base'], 'expiry': call['expiry'], 'cost': round(totalCost, 2), 'strike': call['strike'], 'longBreak':
             round(call['strike'] + costPerShare, 4,), 'shortBreak': round(put['strike'] - costPerShare, 4), 'break%': breakPercent,
             'ppp': round((totalCost / 100) * ppp, 2), 'ppp%': round(ppp, 2)}




if __name__ == "__main__":
    main()
