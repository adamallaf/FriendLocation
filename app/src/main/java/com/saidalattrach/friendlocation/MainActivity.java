package com.saidalattrach.friendlocation;

import android.app.Activity;
import android.app.PendingIntent;
import android.content.Intent;
import android.os.Bundle;

import com.google.android.gms.common.ConnectionResult;
import com.google.android.gms.common.api.GoogleApiClient;

import com.google.android.gms.common.api.PendingResult;
import com.google.android.gms.common.api.ResultCallback;
import com.google.android.gms.location.LocationRequest;
import com.google.android.gms.location.LocationServices;
import com.google.android.gms.location.LocationSettingsRequest;
import com.google.android.gms.location.LocationSettingsResult;

public class MainActivity extends Activity implements GoogleApiClient.ConnectionCallbacks,
        GoogleApiClient.OnConnectionFailedListener
{
    private static final int SETTINGS_REQUEST_CODE = 0;
    private static final int SERVICE_REQUEST_CODE = 1;

    private GoogleApiClient client;
    private LocationRequest locationRequest;

    protected void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        client = new GoogleApiClient.Builder(this)
                .addConnectionCallbacks(this)
                .addOnConnectionFailedListener(this)
                .addApi(LocationServices.API)
                .build();

        locationRequest = new LocationRequest();
        locationRequest.setInterval(10000);
        locationRequest.setFastestInterval(3000);
        locationRequest.setPriority(LocationRequest.PRIORITY_HIGH_ACCURACY);
    }

    protected void onStart()
    {
        super.onStart();
        client.connect();
    }

    protected void onStop()
    {
        super.onStop();
        client.disconnect();
    }

    public void onConnected(Bundle bundle)
    {
        LocationSettingsRequest request = new LocationSettingsRequest.Builder()
                .addLocationRequest(locationRequest).build();

        PendingResult<LocationSettingsResult> result = LocationServices.SettingsApi
                .checkLocationSettings(client, request);

        result.setResultCallback(new ResultCallback<LocationSettingsResult>()
        {
            public void onResult(LocationSettingsResult locationSettingsResult)
            {
                if (locationSettingsResult.getStatus().hasResolution())
                {
                    try
                    {
                        locationSettingsResult.getStatus()
                                .startResolutionForResult(MainActivity.this, SETTINGS_REQUEST_CODE);
                    } catch (Exception ignored) {}
                }
            }
        });
    }

    protected void onActivityResult(int requestCode, int resultCode, Intent data)
    {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == SETTINGS_REQUEST_CODE)
        {
            PendingIntent intent = PendingIntent.getService(MainActivity.this, SERVICE_REQUEST_CODE,
                    new Intent(MainActivity.this, MainService.class), 0);
            try
            {
                LocationServices.FusedLocationApi.requestLocationUpdates(client, locationRequest,
                        intent);
            } catch (SecurityException ignored) {}
        }
    }

    public void onConnectionSuspended(int i) {}

    public void onConnectionFailed(ConnectionResult connectionResult) {}
}
