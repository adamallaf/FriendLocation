package com.saidalattrach.friendlocation;

import android.app.Service;
import android.content.Intent;
import android.location.Location;
import android.os.Binder;
import android.os.Bundle;
import android.os.Handler;
import android.os.HandlerThread;
import android.os.IBinder;
import android.os.Looper;

import com.google.android.gms.common.api.GoogleApiClient;
import com.google.android.gms.common.api.PendingResult;
import com.google.android.gms.common.api.Status;
import com.google.android.gms.location.LocationListener;
import com.google.android.gms.location.LocationRequest;
import com.google.android.gms.location.LocationServices;
import com.google.android.gms.location.LocationSettingsRequest;
import com.google.android.gms.location.LocationSettingsResult;

import java.io.IOException;
import java.net.SocketTimeoutException;

public class MainService extends Service implements LocationListener,
        GoogleApiClient.ConnectionCallbacks
{
    private static final int DEFAULT_UPDATE_INTERVAL = 30;

    private LocalBinder localBinder;

    private LocationRequest locationRequest;
    private GoogleApiClient client;

    private Handler serviceHandler;
    private Handler mainHandler;

    public void onCreate()
    {
        System.out.println("Creating service...");
        localBinder = new LocalBinder();

        HandlerThread thread = new HandlerThread("MainServiceThread");
        thread.start();

        serviceHandler = new Handler(thread.getLooper());
        mainHandler = new Handler(Looper.getMainLooper());
    }

    public int onStartCommand (Intent intent, int flags, int startId)
    {
        System.out.println("Starting service...");
        serviceHandler.post(() ->
        {
            locationRequest = new LocationRequest();

            locationRequest.setInterval(DEFAULT_UPDATE_INTERVAL * 60 * 1000);
            locationRequest.setFastestInterval(DEFAULT_UPDATE_INTERVAL * 60 * 1000);

            locationRequest.setPriority(LocationRequest.PRIORITY_HIGH_ACCURACY);

            client = new GoogleApiClient.Builder(this)
                    .addApi(LocationServices.API)
                    .addConnectionCallbacks(this)
                    .build();
            client.connect();
        });
        return START_STICKY;
    }

    public void onDestroy()
    {
        System.out.println("Destroying service...");
        removeLocationUpdates();
        client.disconnect();

        localBinder = null;
        locationRequest = null;
        client = null;
    }

    public IBinder onBind(Intent intent)
    {
        return localBinder;
    }

    public void requesLocationUpdates(final LocationUpdateCallback callback)
    {
        serviceHandler.post(() ->
        {
            LocationSettingsRequest request = new LocationSettingsRequest.Builder()
                    .addLocationRequest(locationRequest).build();

            PendingResult<LocationSettingsResult> result = LocationServices.SettingsApi
                    .checkLocationSettings(client, request);

            result.setResultCallback((LocationSettingsResult locationSettingsResult) ->
            {
                final Status status = locationSettingsResult.getStatus();
                if (status.isSuccess())
                    requestLocationUpdatesInternal();
                else if (callback != null)
                    mainHandler.post(() -> callback.onLocationUpdate(status));
            });
        });
    }

    private void requestLocationUpdatesInternal()
    {
        try
        {
            serviceHandler.post(() ->
            {
                locationRequest.setInterval(5000);
                locationRequest.setFastestInterval(5000);
                LocationServices.FusedLocationApi.requestLocationUpdates(client,
                        locationRequest, this);
            });
        } catch (SecurityException ignored) {}
    }

    public void onLocationChanged(Location location)
    {
        serviceHandler.post(() -> processLocationResult(location));
    }

    private void processLocationResult(Location location)
    {
        System.out.println("Attempting to send location to the server...");
        try
        {
            TheServed.sendLocationPushQuery(new UserLocation("The Served", location.getLongitude(),
                    location.getLatitude()));
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

    private void removeLocationUpdates()
    {
        try
        {
            LocationServices.FusedLocationApi.removeLocationUpdates(client, this);
        } catch (SecurityException ignored) {}
    }

    public void onConnected(Bundle bundle) {}

    public void onConnectionSuspended(int i) {}

    public class LocalBinder extends Binder
    {
        MainService getService()
        {
            return MainService.this;
        }
    }

    public interface LocationUpdateCallback
    {
        void onLocationUpdate(Status status);
    }

    public void setUpdateInterval(long interval)
    {
        serviceHandler.post(() ->
        {
            locationRequest.setInterval(interval);
            locationRequest.setFastestInterval(interval);
            requestLocationUpdatesInternal();
        });
    }
}
