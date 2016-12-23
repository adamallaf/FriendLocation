package com.saidalattrach.friendlocation;

import android.app.IntentService;
import android.content.Intent;
import android.location.Location;

import com.google.android.gms.location.LocationResult;

public class MainService extends IntentService
{
    public MainService()
    {
        super("Friend Location Service");
    }

    protected void onHandleIntent(Intent intent)
    {
        if (LocationResult.hasResult(intent))
        {
            Location location = LocationResult.extractResult(intent).getLastLocation();

            System.out.print("Location update received: ");
            System.out.print(location.getLongitude());
            System.out.print(", ");
            System.out.println(location.getLatitude());

            // TODO: Send location info to Telegram Bot
        }
        else
            System.out.println("Location update received, but response was empty :(");
    }
}
