package com.saidalattrach.friendlocation;

import android.app.Notification;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Intent;
import android.content.SharedPreferences;
import android.location.Location;
import android.os.Binder;
import android.os.Handler;
import android.os.HandlerThread;
import android.os.IBinder;
import android.os.Looper;
import android.support.v7.app.NotificationCompat;

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

    private boolean permissionNeeded = false;
    private Status resolutionStatus;

    private String username = "The Served";
    private int updateInterval = 60 * 1000;

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
        System.out.println("Starting service...");
        serviceHandler.post(() ->
        {
            // Check if the service is being started by the activity
            if (intent != null)
            {
                updateInterval = intent.getIntExtra("update_interval", 30) * 60 * 1000;
                TheServed.setHost(intent.getStringExtra("ip_address"));
                username = intent.getStringExtra("username");
            }
            else
            {
                SharedPreferences preferences = getSharedPreferences("preferences", 0);
                updateInterval = preferences.getInt("update_interval", 30) * 60 * 1000;
                TheServed.setHost(preferences.getString("ip_address", ""));
                username = preferences.getString("username", "");
            }

            locationRequest.setInterval(updateInterval);
            locationRequest.setFastestInterval(updateInterval);
            if (client.blockingConnect().isSuccess())
            {
                if (checkLocationSettings())
                    requestLocationUpdates();
                else
                    stopSelf();
            }

            PendingIntent pendingIntent = PendingIntent.getActivity(this, 0,
                    new Intent(this, MainActivity.class), 0);

            Notification notification = new NotificationCompat.Builder(this)
                    .setSmallIcon(R.mipmap.ic_launcher)
                    .setContentTitle("Friend Location Service")
                    .setContentText("The Friend Location Service is running")
                    .setContentIntent(pendingIntent)
                    .build();

            startForeground(1, notification);
        });

        return START_STICKY;
    }

    public void onDestroy()
    {
        removeLocationUpdates();
        client.disconnect();
        System.out.println("Destroying service");
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
        System.out.println("Requesting location updates...");
        try
        {
            LocationServices.FusedLocationApi.requestLocationUpdates(client, locationRequest, this);
            permissionNeeded = false;
        }
        catch (SecurityException e)
        {
            permissionNeeded = true;
        }
    }

    private void removeLocationUpdates()
    {
        System.out.println("Removing location updates...");
        try
        {
            LocationServices.FusedLocationApi.removeLocationUpdates(client, this);
        } catch (SecurityException ignored) {}
    }

    public void onLocationChanged(Location location)
    {
        serviceHandler.post(() -> processLocationResult(location));
        removeLocationUpdates();
        serviceHandler.postDelayed(this::requestLocationUpdates, updateInterval);
    }

    private void processLocationResult(Location location)
    {
        System.out.println("Attempting to send location to the server...");
        try
        {
            TheServed.sendLocationPushQuery(new UserLocation(username, location.getLongitude(),
                    location.getLatitude()));
            System.out.println("Location sent to the server");
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
        public void getPermissionStatus(PermissionStatusCallback callback)
        {
            // Lambda-ception...
            // This ensures that permissionNeeded
            // is set correctly when the callback is called
            serviceHandler.post(() ->
                mainHandler.post(() -> callback.onPermissionCheck(permissionNeeded))
            );
        }

        public void getStatus(LocationUpdateCallback callback)
        {
            // Lambda-ception...
            // This ensures that resolutionStatus is not null
            // when the callback is called
            serviceHandler.post(() ->
                mainHandler.post(() -> callback.onLocationUpdate(resolutionStatus))
            );
        }
    }

    public interface LocationUpdateCallback
    {
        void onLocationUpdate(Status status);
    }

    public interface PermissionStatusCallback
    {
        void onPermissionCheck(boolean permissionNeeded);
    }
}
