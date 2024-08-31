from src.data_client.seeking_alpha import SeekingAlpha
from datetime import date

def screener():
    screen = SeekingAlpha()
    screen_df = screen.get_screen_stocks()
    print(screen_df.head())
    screen_df.to_csv(f"data/seeking_alpha_screen_{date.today()}.csv")

if __name__=="__main__":
    screener()