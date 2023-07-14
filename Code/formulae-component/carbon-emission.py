import argparse
import sys

class CarbonEmissionEstimator:
    def __init__(self, PageTransferSize, CableDistance, CarbonIntensityFactor):
        self.PageTransferSize = PageTransferSize
        self.CableDistance = CableDistance
        self.CarbonIntensityFactor = CarbonIntensityFactor
    
    def EstimateEmissions(self):
        try:
            CarbonEmission = (self.PageTransferSize * self.CableDistance * self.CarbonIntensityFactor) * 2
            EnergyConsumptionInkWh = (self.PageTransferSize * 1.8)/100
            self.PrintResult(CarbonEmission, EnergyConsumptionInkWh)

        except Exception as e:
             print(f"An error occurred: {e}")
        return 

    
    def PrintResult(self, CarbonEmission, EnergyConsumptionInkWh):
        try:
            print('--------------------------------------------------------------------------------------------------------------------\n')
            print("Carbon Emission per page views: " + str(CarbonEmission) + " Kg")
            print("Carbon Emission per 1000 views: " + str(CarbonEmission * 1000) + " Kg")
            print('--------------------------------------------------------------------------------------------------------------------\n')
            print("Based on Constants provided by ABA:")
            print("\n")
            print("Energy consumption per page view (kWh): " + str(EnergyConsumptionInkWh))
            print("CO2 per page view from standard grid energy (kg): " + str((EnergyConsumptionInkWh*475)/1000))
            print("Renewable hosting usage estimates: ")
            print("CO2 per page view with 100% renewable hosting (kg): " + str(((EnergyConsumptionInkWh*0.407)*33.4)/1000+((EnergyConsumptionInkWh*0.593)*449)/1000))
            print('--------------------------------------------------------------------------------------------------------------------\n')
        except Exception as e:
            print(f"An error occurred: {e}")
        return


def main():
    """Main Function"""
    try:
        parser = argparse.ArgumentParser(description='Give metrics')
        parser.add_argument('PageTransferSize', type=float, help='Page Transfer Size')
        parser.add_argument('CableDistance', type=int, help='Cable factor/Undersea cable distance')
        parser.add_argument('CarbonIntensityFactor', type=float, help='Carbon Intensity Factor')
        args = parser.parse_args()
        # Loading excel files as dataframes
        ReportEnhancer = CarbonEmissionEstimator(args.PageTransferSize, args.CableDistance, args.CarbonIntensityFactor)
        # Generating merged Dataframe
        ReportEnhancer.EstimateEmissions()

    except Exception as e:
        print("An error occurred: ", e)
        sys.exit(1)

if __name__ == "__main__":
    main()