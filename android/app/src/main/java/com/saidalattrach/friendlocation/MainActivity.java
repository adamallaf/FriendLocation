package com.saidalattrach.friendlocation;

import android.app.Activity;
import android.app.PendingIntent;
import android.content.Intent;
import android.os.Bundle;
import android.support.v7.widget.SwitchCompat;
import android.widget.CompoundButton;
import android.widget.NumberPicker;

import com.google.android.gms.common.ConnectionResult;
import com.google.android.gms.common.api.GoogleApiClient;

import com.google.android.gms.common.api.PendingResult;
import com.google.android.gms.common.api.ResultCallback;
import com.google.android.gms.common.api.Status;
import com.google.android.gms.location.LocationRequest;
import com.google.android.gms.location.LocationServices;
import com.google.android.gms.location.LocationSettingsRequest;
import com.google.android.gms.location.LocationSettingsResult;

public class MainActivity extends Activity implements GoogleApiClient.ConnectionCallbacks,
        GoogleApiClient.OnConnectionFailedListener
{
    private static final int SETTINGS_REQUEST_CODE = 0;
    private static final int SERVICE_REQUEST_CODE = 1;

    private static final int MIN_UPDATE_INTERVAL = 1;
    private static final int MAX_UPDATE_INTERVAL = 120;
    private static final int DEFAULT_UPDATE_INTERVAL = 30;

    private GoogleApiClient client;
    private LocationRequest locationRequest;
    private PendingIntent serviceIntent;

    private SwitchCompat enableToggle;

    protected void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);

        locationRequest = new LocationRequest();

        locationRequest.setInterval(DEFAULT_UPDATE_INTERVAL * 60 * 1000);
        locationRequest.setFastestInterval(DEFAULT_UPDATE_INTERVAL * 60 * 1000);

        locationRequest.setPriority(LocationRequest.PRIORITY_HIGH_ACCURACY);

        serviceIntent = PendingIntent.getService(MainActivity.this, SERVICE_REQUEST_CODE,
                new Intent(this, MainService.class), PendingIntent.FLAG_CANCEL_CURRENT);

        setContentView(R.layout.activity_main);

        enableToggle = (SwitchCompat) findViewById(R.id.enable_update);

        enableToggle.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener()
        {
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked)
            {
                if (isChecked)
                    requesLocationUpdates();
                else
                    removeLocationUpdates();
            }
        });

        NumberPicker picker = (NumberPicker) findViewById(R.id.update_interval_picker);

        picker.setMinValue(MIN_UPDATE_INTERVAL);
        picker.setMaxValue(MAX_UPDATE_INTERVAL);
        picker.setValue(DEFAULT_UPDATE_INTERVAL);

        picker.setOnValueChangedListener(new NumberPicker.OnValueChangeListener()
        {
            public void onValueChange(NumberPicker picker, int oldVal, int newVal)
            {
                newVal *= 60 * 1000;

                locationRequest.setInterval(newVal);
                locationRequest.setFastestInterval(newVal);

                if (enableToggle.isChecked())
                    requesLocationUpdates();
            }
        });
    }

    protected void onStart()
    {
        super.onStart();
        System.out.println("Building client and connecting...");
        client = new GoogleApiClient.Builder(this)
                .addConnectionCallbacks(this)
                .addOnConnectionFailedListener(this)
                .addApi(LocationServices.API)
                .build();
        client.connect();
    }

    protected void onStop()
    {
        super.onStop();
        System.out.println("Disconnecting client...");
        client.disconnect();
    }

    public void onConnected(Bundle bundle)
    {
        if (enableToggle.isChecked())
            requesLocationUpdates();
    }

    private void requesLocationUpdates()
    {
        LocationSettingsRequest request = new LocationSettingsRequest.Builder()
                .addLocationRequest(locationRequest).build();

        PendingResult<LocationSettingsResult> result = LocationServices.SettingsApi
                .checkLocationSettings(client, request);

        result.setResultCallback(new ResultCallback<LocationSettingsResult>()
        {
            public void onResult(LocationSettingsResult locationSettingsResult)
            {
                Status status = locationSettingsResult.getStatus();

                if (status.isSuccess())
                    requestLocationUpdatesInternal();
                else if (status.hasResolution())
                {
                    try
                    {
                        status.startResolutionForResult(MainActivity.this, SETTINGS_REQUEST_CODE);
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
            if (resultCode == RESULT_OK)
                requestLocationUpdatesInternal();
            else
                enableToggle.setChecked(false);
        }
    }

    private void requestLocationUpdatesInternal()
    {
        try
        {
            LocationServices.FusedLocationApi.requestLocationUpdates(client, locationRequest,
                    serviceIntent);
        } catch (SecurityException ignored) {}
    }

    private void removeLocationUpdates()
    {
        System.out.println("Removing location updates...");

        try
        {
            LocationServices.FusedLocationApi.removeLocationUpdates(client, serviceIntent);
        } catch (SecurityException ignored) {}
    }

    public void onConnectionSuspended(int i) {}

    public void onConnectionFailed(ConnectionResult connectionResult) {}
}
