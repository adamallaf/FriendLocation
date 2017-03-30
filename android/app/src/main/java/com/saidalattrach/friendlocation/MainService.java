package com.saidalattrach.friendlocation;

import android.app.Service;
import android.content.Intent;
import android.location.Location;
import android.os.Binder;
import android.os.Handler;
import android.os.HandlerThread;
import android.os.IBinder;
import android.os.Looper;

import com.google.android.gms.common.api.GoogleApiClient;
import com.google.android.gms.common.api.Status;
import com.google.android.gms.location.LocationListener;
import com.google.android.gms.location.LocationRequest;
import com.google.android.gms.location.LocationServices;
import com.google.android.gms.location.LocationSettingsRequest;

import java.io.IOException;
import java.net.SocketTimeoutException;

public class MainService extends Service implements LocationListener
{
    private LocalBinder localBinder;

    private LocationRequest locationRequest;
    private GoogleApiClient client;

    private Handler serviceHandler;
    private Handler mainHandler;

    private Status resolutionStatus;

    private String username = "The Served";

    public void onCreate()
    {
        localBinder = new LocalBinder();

        HandlerThread thread = new HandlerThread("MainServiceThread");
        thread.start();

        serviceHandler = new Handler(thread.getLooper());
        mainHandler = new Handler(Looper.getMainLooper());

        locationRequest = new LocationRequest();

        locationRequest.setPriority(LocationRequest.PRIORITY_HIGH_ACCURACY);

        client = new GoogleApiClient.Builder(this).addApi(LocationServices.API).build();
    }

    public int onStartCommand (Intent intent, int flags, int startId)
    {
        serviceHandler.post(() ->
        {
            // If the service is being started by the activity
            if (intent != null)
            {
                int updateInterval = intent.getIntExtra("UPDATE_INTERVAL", 30);
                locationRequest.setInterval(updateInterval * 60 * 1000);
                locationRequest.setFastestInterval(updateInterval * 60 * 1000);
            }

            if (client.blockingConnect().isSuccess())
            {
                if (checkLocationSettings())
                    requestLocationUpdates();
                else
                    stopSelf();
            }
        });

        return START_STICKY;
    }

    public void onDestroy()
    {
        serviceHandler.post(() ->
        {
            removeLocationUpdates();
            client.disconnect();
            System.out.println("Destroying service");
        });
    }

    public IBinder onBind(Intent intent)
    {
        return localBinder;
    }

    private boolean checkLocationSettings()
    {
        LocationSettingsRequest request = new LocationSettingsRequest.Builder()
                .addLocationRequest(locationRequest).build();

        resolutionStatus = LocationServices.SettingsApi.checkLocationSettings(client, request)
                .await().getStatus();

        return resolutionStatus.isSuccess();
    }

    private void requestLocationUpdates()
    {
        System.out.println("Requesting location updates");
        try
        {
            LocationServices.FusedLocationApi.requestLocationUpdates(client, locationRequest, this);
        } catch (SecurityException ignored) {}
    }

    private void removeLocationUpdates()
    {
        try
        {
            LocationServices.FusedLocationApi.removeLocationUpdates(client, this);
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
            TheServed.sendLocationPushQuery(new UserLocation(username, location.getLongitude(),
                    location.getLatitude()));
            System.out.println("Location sent to the server");
            TheServed.sendLocationPushQuery(new UserLocation(username, (float) location.getLongitude(), (float) location.getLatitude()));
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

    public class LocalBinder extends Binder
    {
        public void getStatus(LocationUpdateCallback callback)
        {
            // Lambda-ception...
            serviceHandler.post(() ->
                mainHandler.post(() -> callback.onLocationUpdate(resolutionStatus))
            );
        }

        public void setUpdateInterval(long interval)
        {
            serviceHandler.post(() ->
            {
                locationRequest.setInterval(interval);
                locationRequest.setFastestInterval(interval);
                requestLocationUpdates();
            });
        }

        public void setUsername(String username)
        {
            MainService.this.username = username;
        }
    }

    public interface LocationUpdateCallback
    {
        void onLocationUpdate(Status status);
    }
}
