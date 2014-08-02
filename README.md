Lifelogger
==========

Track your life like a pro on Google Calendar via your terminal.


## Installation Instructions

  1. Install with pip, the python package manager:
    ```sh
    pip install lifelogger
    ```

  2. Run for the first time, which should initialize the OAuth connection dialog.

    ```sh
    lifelogger now "Started lifelogger"
    ```

    You'll need to click through and accept the app on your Google account. After saying yes, switch back to the terminal and you should see:

    ```sh
    Authentication successful.
    ```

    Followed by:

    ```sh
    Adding 0-minute event >> Started lifelogger
    ```

    And then when that succeeds, a link to the event on the Google Calendar web interface. Congratulations, you can now create events on Google Calendar from your terminal!


## How does it work?

`lifelogger` stores events directly into Google Calendar via its API. It can
also download your entire calendar back to your computer via the "iCal export"
URL that Google provides, and then you can use commands to analyze it locally.
Downloading the entire calendar back makes it a lot faster to perform any
analysis:

![](https://github.com/github/training-kit/blob/master/docs/in-and-out.png)

## Quickstart Guide

For a quick example, let's imagine you want to track your weight with `lifelogger`. It's up to you to develop rules for tracking what you want to, but the suggested system you use is one of hashtags (like on Twitter) to keep your records machine searchable but still quite human readable. `lifelogger` is also aware of common data formats and knows how to search them, so we can just enter our weight in kg

Imagine you've got your scales out, and you weigh yourself - let's record it on the calendar as a 0-minute event:

```sh
lifelogger now "#weight 80.0kg"
```

The event should be added straightforwardly.

Once you get going, you'll probably want to track things quickly, so you won't want to have to `cd` into the `lifelogger` directory every time. You can add an alias in your shell startup file (e.g. `~/.bashrc`, `~/.zshrc`) so that you can always run the command quickly. The recommended alias is `l` (which will be used for the rest of this how-to):

```sh
alias l=lifelogger
```

Now let's download the calendar for analysis. Run:

```sh
l download
```

At this point, you'll be prompted to tell `lifelogger` the private URL for your calendar (unfortunately there is no way to do this with the API). So follow the instructions, heading to the Google Calendar web interface and copying the URL from there. Once you've set that, the download should progress (can take a few seconds):

```sh
Downloading private iCal file...
Download successful!
Converting iCal file into sqlite database...
Imported 7175 events.
```

We've fetched your entire Google Calendar history locally and then converted into a database which can be used to query it quickly. It's good to do this regularly, so you have a backup of your data, as well as being able to analyze all of it (the analysis commands only run on the database version).

By the way, `lifelogger` only stores data in `~/.config/lifelogger`. If you want to erase the calendar file, database, and Google OAuth permissions, just delete the contents of that directory.

Let's run a quick search on all of our `#weight` events:

```sh
l list "#weight"
```

You should see a listing of all your events that match '#weight', with their date/time and the full information. There are plenty more commands to play with, including other options and ways to add events to your calendar, as well as query them in more interesting ways. Have a poke around in the source code to check it out!
