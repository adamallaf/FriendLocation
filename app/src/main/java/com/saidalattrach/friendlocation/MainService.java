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
        LocationResult result = LocationResult.extractResult(intent);

        if (result != null)
        {
            Location location = result.getLastLocation();

            System.out.print(location.getLongitude());
            System.out.print(", ");
            System.out.println(location.getLatitude());

            // TODO: Send location info to Telegram Bot
        }
    }
}
