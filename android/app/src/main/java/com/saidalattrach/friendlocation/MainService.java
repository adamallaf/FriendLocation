package com.saidalattrach.friendlocation;

import android.app.IntentService;
import android.content.Intent;
import android.location.Location;

import com.google.android.gms.location.LocationResult;

import java.io.IOException;
import java.net.SocketTimeoutException;

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

            System.out.println("Attempting to send location to the server...");
            try
            {
                TheServed.sendLocationPushQuery(new UserLocation("The Served",
                        location.getLongitude(), location.getLatitude()));
                System.out.println("Location sent to the server");
                UserLocation[] locs = TheServed.sendLocationPullQuery(new String[] {"The Served"});
                if (locs != null)
                {
                    for (UserLocation l : locs)
                    {
                        System.out.print(l.getLongitude() + ", ");
                        System.out.println(l.getLatitude());
                    }
                }
            }
            catch (SocketTimeoutException e)
            {
                System.out.println("Failed to connect to the server. The server is not respoding.");
                e.printStackTrace();
            }
            catch (IOException e)
            {
                System.out.println("Failed to connect to the server. Check your internet conenction.");
                e.printStackTrace();
            }
        }
        else
            System.out.println("Location update received, but response was empty :(");
    }
}
