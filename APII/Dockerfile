FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS base
USER $APP_UID
WORKDIR /app

FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
ARG BUILD_CONFIGURATION=Release
WORKDIR /src
COPY ["APII/APII.csproj", "APII/"]
RUN dotnet restore "APII/APII.csproj"
COPY . .
WORKDIR "/src/APII"
RUN dotnet build "APII.csproj" -c $BUILD_CONFIGURATION -o /app/build

WORKDIR /src/APII.UnitTests
RUN dotnet restore "APII.UnitTests.csproj"
RUN dotnet test "APII.UnitTests.csproj"
WORKDIR /src/APII

FROM build AS publish
ARG BUILD_CONFIGURATION=Release
RUN dotnet publish "APII.csproj" -c $BUILD_CONFIGURATION -o /app/publish /p:UseAppHost=false

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "APII.dll"]
